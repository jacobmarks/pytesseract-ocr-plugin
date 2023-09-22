"""PyTesseract OCR plugin.

| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import os

import fiftyone as fo
from fiftyone.core.utils import add_sys_path
import fiftyone.operators as foo
from fiftyone.operators import types


def _execution_mode(ctx, inputs):
    delegate = ctx.params.get("delegate", False)

    if delegate:
        description = "Uncheck this box to execute the operation immediately"
    else:
        description = "Check this box to delegate execution of this task"

    inputs.bool(
        "delegate",
        default=False,
        required=True,
        label="Delegate execution?",
        description=description,
        view=types.CheckboxView(),
    )

    if delegate:
        inputs.view(
            "notice",
            types.Notice(
                label=(
                    "You've chosen delegated execution. Note that you must "
                    "have a delegated operation service running in order for "
                    "this task to be processed. See "
                    "https://docs.voxel51.com/plugins/index.html#operators "
                    "for more information"
                )
            ),
        )


def _list_target_views(ctx, inputs):
    has_view = ctx.view != ctx.dataset.view()
    has_selected = bool(ctx.selected)
    default_target = "DATASET"
    if has_view or has_selected:
        target_choices = types.RadioGroup()
        target_choices.add_choice(
            "DATASET",
            label="Entire dataset",
            description="Merge labels for the entire dataset",
        )

        if has_view:
            target_choices.add_choice(
                "CURRENT_VIEW",
                label="Current view",
                description="Merge labels for the current view",
            )
            default_target = "CURRENT_VIEW"

        if has_selected:
            target_choices.add_choice(
                "SELECTED_SAMPLES",
                label="Selected samples",
                description="Merge labels for the selected samples",
            )
            default_target = "SELECTED_SAMPLES"

        inputs.enum(
            "target",
            target_choices.values(),
            default=default_target,
            view=target_choices,
        )
    else:
        ctx.params["target"] = default_target


def _get_target_view(ctx, target):
    if target == "SELECTED_SAMPLES":
        return ctx.view.select(ctx.selected)

    if target == "DATASET":
        return ctx.dataset

    return ctx.view


class OCR(foo.Operator):
    @property
    def config(self):
        _config = foo.OperatorConfig(
            name="run_ocr_engine",
            label="OCR: run optical character recognition on your images",
            dynamic=True,
        )
        _config.icon = "/assets/icon_light.svg"
        return _config

    def resolve_delegation(self, ctx):
        return ctx.params.get("delegate", False)

    def resolve_placement(self, ctx):
        return types.Placement(
            types.Places.SAMPLES_GRID_ACTIONS,
            types.Button(
                label="Detect text in images",
                icon="/assets/icon_light.svg",
                dark_icon="/assets/icon.svg",
                light_icon="/assets/icon_light.svg",
            ),
        )

    def resolve_input(self, ctx):
        inputs = types.Object()
        form_view = types.View(
            label="OCR",
            description=(
                "Run optical character recognition on your images to"
                "detect text with PyTesseract"
            ),
        )
        _execution_mode(ctx, inputs)
        _list_target_views(ctx, inputs)
        return types.Property(inputs, view=form_view)

    def execute(self, ctx):
        dataset = ctx.dataset
        dataset.compute_metadata()

        view = _get_target_view(ctx, ctx.params["target"])

        with add_sys_path(os.path.dirname(os.path.abspath(__file__))):
            # pylint: disable=no-name-in-module,import-error
            from ocr_engine import get_ocr_detections

            for sample in view.iter_samples(autosave=True):
                word_dets, block_dets = get_ocr_detections(sample)
                sample["pt_word_predictions"] = word_dets
                sample["pt_block_predictions"] = block_dets
        dataset.add_dynamic_sample_fields()
        ctx.trigger("reload_dataset")


def register(plugin):
    plugin.register(OCR)

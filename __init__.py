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
            description="Run OCR on the entire dataset",
        )

        if has_view:
            target_choices.add_choice(
                "CURRENT_VIEW",
                label="Current view",
                description="Run OCR on the current view",
            )
            default_target = "CURRENT_VIEW"

        if has_selected:
            target_choices.add_choice(
                "SELECTED_SAMPLES",
                label="Selected samples",
                description="Run OCR on the selected samples",
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


def _handle_prediction_fields(ctx, inputs):
    obj = types.Object()
    obj.bool(
        "store_word_preds",
        label="Store word predictions?",
        default=False,
        view=types.SwitchView(space=4),
    )
    obj.bool(
        "store_block_preds",
        label="Store block predictions?",
        default=True,
        view=types.SwitchView(space=4),
    )
    inputs.define_property("prediction_field_types", obj)

    pfts = ctx.params.get("prediction_field_types", {})
    store_word_preds = pfts.get("store_word_preds", False)
    store_block_preds = pfts.get("store_block_preds", True)

    if not store_word_preds and not store_block_preds:
        inputs.view(
            "warning",
            types.Warning(
                label="Not storing any predictions",
                description=(
                    "You have chosen not to store any predictions. "
                    "You must store at least one type of prediction to "
                    "use the `OCR` operation. "
                ),
            ),
        )

    if store_word_preds:
        inputs.str(
            "word_predictions_field",
            label="Word predictions field",
            default="pt_word_predictions",
            description="The field in which to store the word predictions",
            required=True,
        )

    if store_block_preds:
        inputs.str(
            "block_predictions_field",
            label="Block predictions field",
            default="pt_block_predictions",
            description="The field in which to store the block predictions",
            required=True,
        )


def _get_prediction_fields(ctx):
    word_preds_field = ctx.params.get("word_predictions_field", None)
    block_preds_field = ctx.params.get("block_predictions_field", None)
    return word_preds_field, block_preds_field


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
                "Run optical character recognition on your images to "
                "detect text with PyTesseract"
            ),
        )
        _execution_mode(ctx, inputs)
        _list_target_views(ctx, inputs)
        _handle_prediction_fields(ctx, inputs)
        return types.Property(inputs, view=form_view)

    def execute(self, ctx):
        dataset = ctx.dataset
        dataset.compute_metadata()

        view = _get_target_view(ctx, ctx.params["target"])

        word_preds_field, block_preds_field = _get_prediction_fields(ctx)

        with add_sys_path(os.path.dirname(os.path.abspath(__file__))):
            # pylint: disable=no-name-in-module,import-error
            from ocr_engine import get_ocr_detections

            for sample in view.iter_samples(autosave=True):
                word_dets, block_dets = get_ocr_detections(sample)
                if word_preds_field:
                    sample[word_preds_field] = word_dets
                if block_preds_field:
                    sample[block_preds_field] = block_dets
        dataset.add_dynamic_sample_fields()
        ctx.trigger("reload_dataset")


def register(plugin):
    plugin.register(OCR)

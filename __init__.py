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


class OCR(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="run_ocr_engine",
            label="OCR: run optical character recognition on your images",
            icon="/assets/icon_light.svg",
            dynamic=True,
        )

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
        return types.Property(inputs, view=form_view)

    def execute(self, ctx):
        dataset = ctx.dataset
        dataset.compute_metadata()

        with add_sys_path(os.path.dirname(os.path.abspath(__file__))):
            # pylint: disable=no-name-in-module,import-error
            from ocr_engine import get_ocr_detections

            for sample in dataset.iter_samples(autosave=True):
                word_dets, block_dets = get_ocr_detections(sample)
                sample["pt_word_predictions"] = word_dets
                sample["pt_block_predictions"] = block_dets
        dataset.add_dynamic_sample_fields()
        ctx.trigger("reload_dataset")


def register(plugin):
    plugin.register(OCR)

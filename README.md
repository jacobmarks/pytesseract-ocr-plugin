## PyTesseract Optical Character Recognition Plugin

<img width="1727" alt="funsd_predictions" src="https://github.com/jacobmarks/pytesseract-ocr-plugin/assets/12500356/1bda669c-f2f8-456f-912f-c3f6a6a0fadd">

### Updates

- **2023-10-19**: Added support for customizing prediction fields, and embedded field for OCR text.

This plugin is a Python plugin that allows you to perform optical character
recognition on documents using PyTesseract — the Python bindings for the
Tesseract OCR engine!

It demonstrates how to do the following:

- Use FiftyOne for natural language document understanding
- Place your operator as a button in the App via a Python plugin
- Delegate the execution of time-consuming tasks

## Installation

```shell
fiftyone plugins download https://github.com/jacobmarks/pytesseract-ocr-plugin
```

You will also need to install the plugin's requirements:

```shell
pip install -r requirements.txt
```

## Operators

### `run_ocr_engine`

- Runs the PyTesseract OCR engine on the documents in the dataset, converts the
  results to FiftyOne labels, and stores individual word predictions as well
  as block-level predictions on the dataset.

## Usage

You can access the operator via the App's action menu, or by pressing the "`"
key on your keyboard and selecting the operator from the dropdown menu.

If you have a view loaded and/or samples selected, the operator will give you
the option to run the OCR engine on only those samples or on the entire dataset.

You can either choose to run the operator in the foreground, or to delegate the
execution of the operator to a background job.

![ocr_queue_job](https://github.com/jacobmarks/pytesseract-ocr-plugin/assets/12500356/2ab239c1-8d37-44a7-b8d6-93285afe7f08)

💡 Once you've generated OCR predictions, you can search through them using the [Keyword Search plugin](https://github.com/jacobmarks/keyword-search-plugin)!

<img width="1727" alt="funsd_block_predictions" src="https://github.com/jacobmarks/pytesseract-ocr-plugin/assets/12500356/a7b6e81f-7a1e-4663-8ae9-c32c3266015d">

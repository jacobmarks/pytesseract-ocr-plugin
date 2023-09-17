## PyTesseract Optical Character Recognition Plugin

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

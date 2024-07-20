# CKEditor Track Changes Audit API

This is an implementation for CKEditor Track Changes plugin, to audit every user's input inside every editor.

### Project Init
```
/bin/bash

# create a python virtual environment and install dependencies

$ python -m venv venv 
$ source venv/scripts/activate
$ pip install -r requirements.txt

# run project

$ uvicorn main:app --reload
```
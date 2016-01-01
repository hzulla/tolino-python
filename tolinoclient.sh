#!/bin/bash

## script to be placed e.g. in /usr/local/bin
# adjust whereever it's installed
pushd /home/jan/projs/tolino/tolino-python
PYTHONPATH=. python2 tolinoclient.py --config ~/.tolinoclient $*
popd

#!/bin/bash
export PYTHONPATH=$PYTHONPATH:/home/oliver/Dropbox/whitepine/lib;
source ~/env/pydata/bin/activate
/home/oliver/bin/wpcmd import
python /home/oliver/src/blue-meth/ipynb/rapnet_loader.py
python /home/oliver/Dropbox/whitepine/lib/cron.py

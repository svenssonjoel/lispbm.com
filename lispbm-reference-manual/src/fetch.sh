#!/bin/bash


cp ../../../lispbm/doc/displayref.md .
cp ../../../lispbm/doc/dynref.md .
cp ../../../lispbm/doc/lbmref.md .
cp ../../../lispbm/doc/runtimeref.md .
cp ../../../lispbm/doc/ttfref.md .

# Get the  vesc express display manual
wget https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/README.md
mv README.md vesc-express-display.md

# Get the vesc LispBM CORE reference manual 
wget https://raw.githubusercontent.com/vedderb/bldc/refs/heads/master/lispBM/README.md
mv README.md vesc-lisp-documentation.md


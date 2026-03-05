#!/bin/bash


cp ../../../lispbm/doc/displayref.md .
cp ../../../lispbm/doc/dynref.md .
cp ../../../lispbm/doc/lbmref.md .
cp ../../../lispbm/doc/runtimeref.md .
cp ../../../lispbm/doc/ttfref.md .
cp ../../../lispbm/doc/arrayref.md .
cp ../../../lispbm/doc/dspref.md .
cp ../../../lispbm/doc/mathref.md .
cp ../../../lispbm/doc/mutexref.md .
cp ../../../lispbm/doc/setref.md .
cp ../../../lispbm/doc/stringref.md .
cp ../../../lispbm/doc/randomref.md .

# Copy images from lispbm doc
cp -r ../../../lispbm/doc/images ./images


# Get the vesc express display manual
wget https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/README.md
mv README.md vesc-express-display.md

# Get the vesc express display resource images
mkdir -p resources
wget -P resources https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/resources/line_attributes.jpg
wget -P resources https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/resources/circle_attributes.jpg
wget -P resources https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/resources/circle_sector_attributes.jpg
wget -P resources https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/resources/circle_segment_attributes.jpg
wget -P resources https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/resources/triangle_attributes.jpg
wget -P resources https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/resources/rectangle_attributes.jpg
wget -P resources https://raw.githubusercontent.com/vedderb/vesc_express/refs/heads/main/main/display/resources/blit_attributes.jpg

# Get the vesc LispBM CORE reference manual
wget https://raw.githubusercontent.com/vedderb/bldc/refs/heads/master/lispBM/README.md
mv README.md vesc-lisp-documentation.md


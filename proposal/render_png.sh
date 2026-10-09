#!/bin/bash
# Render architecture.svg to architecture.png.
#
# qlmanage only emits square thumbnails and crops anything that overflows, so
# the SVG is first wrapped in a square canvas with the diagram centred.
set -e
cd "$(dirname "$0")"

W=$(sed -n 's/.*<svg[^>]*width="\([0-9]*\)".*/\1/p' architecture.svg | head -1)
H=$(sed -n 's/.*<svg[^>]*height="\([0-9]*\)".*/\1/p' architecture.svg | head -1)
SIDE=$(( W > H ? W : H ))
OX=$(( (SIDE - W) / 2 ))
OY=$(( (SIDE - H) / 2 ))

cat > .preview.svg <<SVG
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="$SIDE" height="$SIDE" viewBox="0 0 $SIDE $SIDE">
  <rect width="$SIDE" height="$SIDE" fill="#FFFFFF"/>
  <image xlink:href="architecture.svg" x="$OX" y="$OY" width="$W" height="$H"/>
</svg>
SVG

rm -f architecture.png .preview.svg.png
qlmanage -t -s 1600 -o . .preview.svg >/dev/null 2>&1
mv .preview.svg.png architecture.png
rm -f .preview.svg
echo "architecture.png written ($(sips -g pixelWidth -g pixelHeight architecture.png | tail -2 | tr -d ' \n'))"

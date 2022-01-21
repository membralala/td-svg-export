# svg_plot

This is a TouchDesigner component, which provides a .svg export for SOP 
components. It acts like a snapshot in that it outputs the momentary state of 
the connected SOPs.

The component was inspired by Matthew Ragan's implementation 
(see [sop-to-svg](https://github.com/raganmd/touchdesigner-sop-to-svg)), 
but it implements a quite different set of features, e.g. polygon and 
polyline colors, strokewidth and multi-layer-settings for SOP composition. 

## Install 

You can download the .tox-file from the build folder. At the moment you'll 
have to install the [svgwrite](https://svgwrite.readthedocs.io/en/latest/index.html) 
package manually to a python version, which is linked to your TouchDesigner 
version.

## Version Support 
The component was tested with 2021.15800 (python3.7) as well as 
2021.16270 (python3.9). It should work with previous TD-releases, which use 
python3.7.
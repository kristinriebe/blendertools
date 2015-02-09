

Blender Tools
==============

A collection of Python scripts to make (my) life easier with Blender.

Some scripts are generic enough to be useful for other people as well. Others are tuned to a very specific task, but still contain some useful code-snippets.

There's no guarantee for my scripts to work; feel free to use them, but at your own risk.

For questions, comments, suggestions, please contact me at
Kristin Riebe, kriebe@aip.de


## ShiftKeyframes.py
Shift keyframes in order to speed-up/slow-down a movie
or give time for another sequence of animations in between.

### RaveStars2Mesh.py
Read points (RAVE-stars) from a csv-file into vertices of mesh-objects.
Use their 3D coordinates for positions in Blender and their 
radial velocities for color. This should in principle also work for other star catalogs, as long as galactic coordinates and distances are given. You would need to adjust the column names and coloring.
I've used it for up to 1 million stars without problems, but performance will probably go down rapidly with larger catalogs.

[<img class="header" src="https://www.rave-survey.org/project/wp-content/uploads/ravestars-map-zoomout-2d.png](ravestars-image.png)

An example file with RAVE-stars extracted from the RAVE database, DR4 (https://www.rave-survey.org/query) is also included:
`ravestars-demo.csv`.

A tutorial for using this script to create a nice animation is given here:
https://escience.aip.de/visualisation/movies/blender-ravestars/

The final animation for flying around the RAVE star distribution is available here:
https://www.rave-survey.org/project/gallery/movies/#RAVE-flight



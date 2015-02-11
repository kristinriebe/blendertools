#!BPY
"""
Read points (RAVE-stars) from a csv-file into vertices of mesh-objects.
Use their 3D coordinates for positions in Blender and their
radial velocities for color.
"""
# It's slow if creating one object per point,
# so for stars I append the points as vertices to meshes
# which have a halo-material.
# This means that all stars belonging to the same
# mesh will have the same material and thus color.
#
# Kristin Riebe, E-Science at AIP, kriebe@aip.de, Oct. 2014
#
# TODO:
# - properly clean up unused lists (lines, stars)
#
#
# Updates:
#   16.12.2014: properly read csv-files
#   19.01.2015: delete unused materials


import bpy
import os
import sys
import fnmatch
from mathutils import Vector, Color
from math import sin, cos, pi
import csv


def get_objects(namepattern):
    """Get objects from all scenes matching the namepattern.
    namepattern -- string regular expression
    """

    objects = [obj for obj in bpy.data.objects
               if fnmatch.fnmatchcase(obj.name, namepattern)]

    # if only selectable and not-hidden objects, use:
    #     bpy.ops.object.select_pattern(pattern=name)
    # if only objects of current scene, use:
    #     bpy.context.scene.objects
    return objects


def delete_objects(objects):
    """ Delete given objects and their data blocks"""
    # Also deletes hidden or unselectable objects
    # Could accelerate this by first selecting all
    # matching objects and then calling bpy.ops.object.delete()
    # once for all.

    bpy.ops.object.select_all(action='DESELECT')

    i = 0
    for obj in objects:

        if obj.hide_select is True:
            obj.hide_select = False
        obj.select = True
        i = i + 1

    # Delete all selected objects
    bpy.ops.object.delete()

    print("%d objects were deleted." % i)

    return


def delete_unused_meshes():
    """Delete unused meshes"""
    # Use this after deleting objects.

    i = 0
    for m in bpy.data.meshes:
        if m.users == 0:
            name = m.name
            bpy.data.meshes.remove(m)
            i = i + 1

            print("Deleted mesh ", name)

    print("%d meshes were deleted." % i)


def delete_unused_materials():
    """Delete all unused materials."""
    # This is done anyway when closing and reopening Blender or reloading
    # the blend-file.
    # But since one may want to rerun this script many times, it can be
    # nicer to remove the unused materials automatically, after deleting
    # objects.
    i = 0
    for mat in bpy.data.materials:
        if mat.users == 0:

            name = mat.name
            bpy.data.materials.remove(mat)
            i = i + 1

            print("Deleted material ", name)

    print("%d materials were deleted." % i)
    return


def make_halo_material(matname, col, size):
    """Function for basic material creation

    matname -- name for material
    col -- mathutils.Color()-object, RGB-triplet for diffuse color
    size -- halo-size
    """

    mat = bpy.data.materials.new(matname)
    mat.diffuse_color = [col.r, col.g, col.b]
    #mat.use_transparency = True
    #mat.alpha = 0

    mat.type = 'HALO'
    mat.halo.size = size

    return mat


def read_daiquiri_csv(filename):
    """Read content of file into a dictionary,
    with keys taken from first row,
    use csv-module for this.
    Assumes a "usual" csv-file, as returned by Daiquiri web
    interface, which is also used for RAVE-Database
    """

    if (os.path.isfile(filename)):
        pass
    else:
        print("File %s does not exist!" % filename)
        raise RuntimeError("Stopping script because file was not found.")

    lines = []
    with open(filename, newline='') as csvfile:
        headerFlag = csv.Sniffer().has_header(csvfile.read(1024))
        csvfile.seek(0)
        if (not headerFlag):
            print("No header found in csv file!")
            raise RuntimeError("Stopping script because file has no proper \
                               header.")

        reader = csv.DictReader(csvfile, delimiter=',')

        for r in reader:
            lines.append(r)
            pass

    return lines


def adjust_values(lines):
    """Go through lines of read file,
    pick only the interesting values,
    convert to cartesian coordinates,
    return as list of dictionaries
    """

    stars = []
    for line in lines:
        RAdeg = float(line['RAdeg'])
        DEdeg = float(line['DEdeg'])

        Glon = float(line['Glon'])
        Glat = float(line['Glat'])

        dist = line['dist']
        if (dist):
            dist = float(dist)
        else:
            dist = 0

        hrv = line['HRV']
        if (hrv):
            hrv = float(hrv)
        else:
            hrv = 0

        teff = line['Teff_K']
        if (teff):
            teff = float(teff)
        else:
            teff = 0

        # convert from galactic to cartesian
        phi = Glon/360.*2*pi
        theta = (90 - Glat)/180.*pi
        r = dist

        star = {}
        star['x'] = r*cos(phi)*sin(theta)
        star['y'] = r*sin(phi)*sin(theta)
        star['z'] = r*cos(theta)

        star['teff'] = teff
        star['hrv'] = hrv

        stars.append(star)

    return stars


def create_mesh(origin, verts, mat, name):
    """Create a mesh from list of vertices only

    origin -- origin of the mesh
    verts -- list of vertices of the mesh
    mat -- material-object, for assigning the proper material
    name -- desired name for the mesh-object
    """

    bpy.ops.object.add(type='MESH', location=(origin))
    obj = bpy.context.object
    obj.name = name
    m = obj.data
    m.from_pydata(verts, [], [])
    m.update()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Assign material
    bpy.ops.object.material_slot_remove()
    obj.data.materials.append(mat)


def create_hrv_meshes(starlist, origin, halosize, posfac):
    """Create vertex-lists for stars,
    distribute stars according to their HRV-value
    """

    verts_r = []
    verts_o = []
    verts_y = []
    verts_c = []
    verts_b = []

    i = 0
    for star in starlist:

        x = star['x']*posfac
        y = star['y']*posfac
        z = star['z']*posfac

        radvel = star['hrv']
        if radvel > 50:
            verts_r.append((x, y, z))
        elif radvel > 10:
            verts_o.append((x, y, z))
        elif radvel > -10:
            verts_y.append((x, y, z))
        elif radvel > -50:
            verts_c.append((x, y, z))
        else:
            verts_b.append((x, y, z))

        i = i + 1
        if (i % 10000 == 0):
            print("Star %d added to vertices." % i)

    # Define the HRV colors
    red = Color((1, 0, 0))
    orange = Color((1, 0.4, 0))
    yellow = Color((1, 1, 0))
    cyan = Color((0, 1, 1))
    blue = Color((0, 0, 1))

    # Create corresponding materials
    matred = make_halo_material('Mesh-red', red,  halosize)  # hrv > 50
    matorange = make_halo_material('Mesh-orange', orange,  halosize)
    matyellow = make_halo_material('Mesh-yellow', yellow, halosize)
    matcyan = make_halo_material('Mesh-cyan', cyan, halosize)
    matblue = make_halo_material('Mesh-blue', blue, halosize)

    # Create meshes for each group of vertices
    create_mesh(origin, verts_r, matred, 'stars-red')
    create_mesh(origin, verts_o, matorange, 'stars-orange')
    create_mesh(origin, verts_y, matyellow, 'stars-yellow')
    create_mesh(origin, verts_c, matcyan, 'stars-cyan')
    create_mesh(origin, verts_b, matblue, 'stars-blue')

    print("HRV-meshes are created.")


if __name__ == '__main__':

    # Scaling factor to fit data to scene
    posfac = 1.8

    # Define size of halo-dots
    halosize = 0.015

    # Origin of the distribution
    origin = Vector((0, 0, 0))

    # File path
    #dirname = "C:\\Users\\..."  # for Windows users
    dirname = "./examples/"
    filename = 'ravestars-demo.csv'
    filename = dirname+filename

    # Deselect everything before deleting
    bpy.ops.object.select_all(action='DESELECT')

    # Delete everything we don't need anymore or want to recreate
    # Be careful to not remove more than you want!
    objects = get_objects('stars-*')
    delete_objects(objects)

    delete_unused_meshes()

    # Delete unused materials. This would also be done automatically
    # when restarting Blender or reloading the file.
    delete_unused_materials()

    # Read data from file, adjust values
    lines = read_daiquiri_csv(filename)
    starlist = adjust_values(lines)
    del lines[:]

    # Go through the stars, sort them by radial velocity and
    # add them to corresponding meshes
    create_hrv_meshes(starlist, origin, halosize, posfac)
    del starlist[:]

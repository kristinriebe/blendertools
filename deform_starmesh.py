#!BPY
"""Move stars (vertices of a mesh) to different forms,
e.g. flat map or sphere, for nice shape-transformation
animations."""
# I assume that the stars are vertices of a few meshes,
# as created by ravestars_mesh.py,
# so I need to move vertices of a mesh, not objects.
# Thus use shapekeys here.
#
# Kristin Riebe, E-Science at AIP, kriebe@aip.de, 27.10.2014

import bpy
import fnmatch
from math import sqrt, acos, atan2, pi


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


def shapekey_vertices_to_sphere(obj, keyname, parameters):
    """Move vertices of mesh to a sky-sphere, using shapekey
    obj  -- mesh-object with stars as vertices
    keyname -- name for shapekey (e.g. 'KeySphere')
    parameters -- dictionary of necessary parameters,
                  here: rsphere for radius of sphere
    """

    rsphere = parameters["rsphere"]

    bpy.ops.object.select_all(action='DESELECT')

    print("Adding sphere-shapekey for ", obj.name)
    m = bpy.data.objects[obj.name]

    obj.select = True

    # Add shape keys for modifying vertices of the mesh
    shapekey = m.shape_key_add(name=keyname, from_mix=True)
    shapekey.value = 1

    for p in shapekey.data:

        r = sqrt(p.co.x*p.co.x + p.co.y*p.co.y + p.co.z*p.co.z)

        scale = rsphere*1./r

        p.co.x = p.co.x * scale
        p.co.y = p.co.y * scale
        p.co.z = p.co.z * scale

    shapekey.value = 0
    m.active_shape_key_index = 0
    obj.select = False

    return shapekey


def shapekey_vertices_to_map(obj, keyname, parameters):
    """Move vertices of mesh to a flat, equirectangular map
    obj  -- mesh-object with stars as vertices
    keyname -- name for shapekey
    parameters -- dictionary of necessary parameters,
                  here:
                  mapw -- width of the map
                  maph -- height of the map
    """

    mapw, maph = parameters["mapw"], parameters["maph"]

    bpy.ops.object.select_all(action='DESELECT')

    print("Adding map-shapekey for ", obj.name)
    m = bpy.data.objects[obj.name]

    obj.select = True

    # Add shape keys for modifying vertices of the mesh
    shapekey = m.shape_key_add(name=keyname, from_mix=True)
    shapekey.value = 1

    for p in shapekey.data:

        r = sqrt(p.co.x*p.co.x + p.co.y*p.co.y + p.co.z*p.co.z)

        theta = acos(p.co.z/r)
        phi = atan2(p.co.y, p.co.x)

        p.co.x = -(phi/(2*pi)*mapw)  # - 0.5*mapw
        p.co.y = 0
        p.co.z = -(theta/(pi)*maph - 0.5*maph)

    shapekey.value = 0
    m.active_shape_key_index = 0

    obj.select = False

    return shapekey


def make_basis_shapekeys(objects, basisname):
    """Create basis shapekey for matching objects
    objects -- list of objects to be used
    basisname -- name for basis shapekey
    """

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern=namepattern)
    objects = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')

    for obj in objects:
        print("Adding basis shapekey for ", obj.name)
        m = bpy.data.objects[obj.name]
        obj.select = True

        basis = m.shape_key_add(name=basisname)

    return


def make_shapekeys(objects, keyname, formtype, parameters):
    """Create shapekeys for given formtype for all matching objects
    objects    -- list of objects to be used
    keyname    -- name for shapekey
    formtype   -- type of form, e.g. 'SPHERE' or 'MAP'
    parameters -- dictionary of necessary parameters, e.g. rsphere, maph;
                  see individual functions for what is needed.
    """

    bpy.ops.object.select_all(action='DESELECT')

    for obj in objects:
        m = bpy.data.objects[obj.name]
        obj.select = True

        # Add shapekeys depending on given formtype
        if formtype == 'SPHERE':
            key = shapekey_vertices_to_sphere(obj, keyname, parameters)
        elif formtype == 'MAP':
            key = shapekey_vertices_to_map(obj, keyname, parameters)
        else:
            raise RuntimeError("There is no function implemented for \
                               formtype='%s' yet." % formtype)

    return


def delete_shapekeys(objects):
    """Delete shapekeys of objects"""

    bpy.ops.object.select_all(action='DESELECT')

    for obj in objects:
        # Select, set active, then delete all shapekeys
        obj.select = True
        bpy.context.scene.objects.active = obj

        if obj.data.shape_keys is not None:
            bpy.ops.object.shape_key_remove(all=True)
            print("Shapekeys for %s deleted." % obj.name)

        obj.select = False

    return


def add_shape_animation(objects, keyname0, iframe0, keyname1, iframe1):
    """Add animation keyframes for shapekeys
    objects    -- list of objects to be used
    keyname0 -- name of basis/previous shapekey
    iframe0 -- frame at which new shapekey value is 0, keyframed
    keyname1 -- name of new shapekey
    iframe1 -- frame at which new shape gets value 1, keyframed
    """

    bpy.ops.object.select_all(action='DESELECT')

    for obj in objects:
        m = bpy.data.objects[obj.name]

        # Select the object
        obj.select = True

        # Set the keyframes for this object
        keyblocks = m.data.shape_keys.key_blocks
        key0 = keyblocks[keyname0]
        key1 = keyblocks[keyname1]

        # Initial shape, value of new shapekey is 0
        iframe = iframe0
        key0.value = 1
        key1.value = 0
        key0.keyframe_insert(data_path="value", frame=iframe)
        key1.keyframe_insert(data_path="value", frame=iframe)

        # New shape with key1
        iframe = iframe1
        key0.value = 0
        key1.value = 1
        key0.keyframe_insert(data_path="value", frame=iframe)
        key1.keyframe_insert(data_path="value", frame=iframe)

        obj.select = False

    return


if __name__ == '__main__':

    # Set parameters: sphere radius, width and height of flat map
    rsphere = 2.

    mapw = 7.5
    maph = 4.5

    # Set string pattern for the star-meshes
    namepattern = 'stars-*'

    # Get objects based on namepattern
    objects = get_objects(namepattern)

    # Set names for shapekeys (just for user convenience)
    basisname = 'Basis'
    mapkeyname = 'KeyMap'
    spherekeyname = 'KeySphere'

    # Delete *all* shapekeys and animation keyframes.
    # Be careful: this may do more than you want.
    delete_shapekeys(objects)

    # Make basis shapekey
    make_basis_shapekeys(objects, basisname)

    # Add sphere-shapekey
    parameters = {"rsphere": rsphere}
    make_shapekeys(objects, spherekeyname, 'SPHERE', parameters)

    # Add map-shapekey
    parameters = {"mapw": mapw, "maph": maph}
    make_shapekeys(objects, mapkeyname, 'MAP', parameters)

    # Add animations. Go backwards, because want initial distribution
    # at the end.

    # Set keyframes for animations
    imap1 = 0
    imap2 = 30
    isphere1 = 100
    isphere2 = 170
    ibasis = 230

    add_shape_animation(objects, basisname, ibasis, spherekeyname, isphere2)
    add_shape_animation(objects, spherekeyname, isphere1, mapkeyname, imap2)

    print("\nDone.")

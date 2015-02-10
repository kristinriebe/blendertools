#!BPY
"""Move stars (vertices of a mesh) to different forms, 
e.g. flat map or sphere, for nice shape-transformation 
animations."""
# I assume that the stars are vertices of a few meshes, 
# as created by RaveStars2Mesh.py, 
# so I need to move vertices of a mesh, not objects. 
# Thus use shapekeys here.
#
# Kristin Riebe, 27.10.2014

import bpy
from math import *

def ShapekeyVerticesToSphere(obj, keyname, parameters):
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


def ShapekeyVerticesToMap(obj, keyname, parameters):
    """Move vertices of mesh to a flat, equirectangular map
    obj  -- mesh-object with stars as vertices
    keyname -- name for shapekey
    parameters -- dictionary of necessary parameters,
                  here:
                  mapw -- width of the map
                  maph -- height of the map
    """
    
    mapw = parameters["mapw"]
    maph = parameters["maph"]
    
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
        
        p.co.x = -(phi/(2*pi)*mapw) #- 0.5*mapw
        p.co.y = 0
        p.co.z = -(theta/(pi)*maph - 0.5*maph)
        
    shapekey.value = 0
    m.active_shape_key_index = 0
    obj.select = False
    
    return shapekey


def makeBasisShapekeys(namepattern, basisname):
    """Create basis shapekey for matching objects"""   
    
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

def makeShapekeys(namepattern, keyname, formtype, parameters):
    """Create shapekeys of for given formtype for all matching objects
    namepattern -- string pattern for selecting objects by name
    keyname     -- name of shapekey
    formtype    -- type of form, e.g. 'SPHERE' or 'MAP'
    parameters  -- dictionary of necessary parameters, e.g. rsphere, maph; 
                   see individual functions for what is needed.
    """   

    bpy.ops.object.select_all(action='DESELECT')  
    bpy.ops.object.select_pattern(pattern=namepattern)
    objects = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
         
    for obj in objects: 
        m = bpy.data.objects[obj.name]
        obj.select = True
    
        # Add shapekeys depending on given formtype        
        if formtype == 'SPHERE':
            key = ShapekeyVerticesToSphere(obj, keyname, parameters)
        elif formtype == 'MAP':
            key = ShapekeyVerticesToMap(obj, keyname, parameters)
        else:
            raise RuntimeError("There is no function implemented for formtype='%s' yet." % formtype)
        
    return


def deleteShapeKeys(namepattern):
    """Delete shapekeys of objects matching namepattern"""
    
    bpy.ops.object.select_all(action='DESELECT')  
    bpy.ops.object.select_pattern(pattern=namepattern)
    objects = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
    
    for obj in objects: 
        # Select, set active, then delete all shapekeys
        obj.select = True
        bpy.context.scene.objects.active = obj  
           
        if obj.data.shape_keys:
            bpy.ops.object.shape_key_remove(all=True)
            print("Shapekeys for %s deleted." % obj.name)

        obj.select = False

    return        

                  
def addShapeAnimation(namepattern, keyname0, iframe0, keyname1, iframe1):
    """Add animation keyframes for shapekeys
    namepattern -- string pattern for selecting objects by name
    keyname0 -- name of basis/previous shapekey
    iframe0 -- frame at which new shapekey value is 0, keyframed
    keyname1 -- name of new shapekey
    iframe1 -- frame at which new shape gets value 1, keyframed
    """

    bpy.ops.object.select_all(action='DESELECT')  
    bpy.ops.object.select_pattern(pattern=namepattern)
    objects = bpy.context.selected_objects
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
    
    # Set string pattern for the star-meshs
    namepattern='stars-*'

    # Set names for shapekeys (just for user convenience)
    basisname='Basis'
    mapkeyname='KeyMap'
    spherekeyname='KeySphere'
    
    # Delete *all* shapekeys and animation keyframes.
    # Be careful: this may do more than you want.
    deleteShapeKeys(namepattern)
    
    # Make basis shapekey
    makeBasisShapekeys(namepattern, basisname)

    # Add sphere-shapekey
    parameters = {"rsphere": rsphere}
    makeShapekeys(namepattern, spherekeyname, 'SPHERE', parameters)

    # Add map-shapekey
    parameters = {"mapw": mapw, "maph": maph}
    makeShapekeys(namepattern, mapkeyname, 'MAP', parameters)
    
    
    # Add animations. Go backwards, because want initial distribution
    # at the end.
    
    # Set keyframes for animations
    imap1 = 0
    imap2 = 30
    isphere1 = 100
    isphere2 = 170
    ibasis = 230
    
    addShapeAnimation(namepattern, basisname, ibasis, spherekeyname, isphere2)
    addShapeAnimation(namepattern, spherekeyname, isphere1, mapkeyname, imap2)
       
    
    print("\nDone.")
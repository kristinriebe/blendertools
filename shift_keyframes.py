#!BPY

""" Shift keyframes in order to speed-up/slow-down a movie
or give time for another sequence of animations in between.
"""
#
# Kristin Riebe, E-Science at AIP, kriebe@aip.de, 04.02.2015
#
# NOTE: This can break your animation completely, if keyframes
#       'overtake' one another. There's no error handling included here.
# NOTE: Only works properly for fcurves with bezier-shape or poly-curves.
#       Fcurve-modifiers are not taken into account.
#
# TODO: Maybe only stretch keyframes with data_path location etc.
# for material/texture fades, keep the distance, but
# shift the initial keyframe?


import bpy
import fnmatch


def get_actions_for_objects(namepattern="*"):
    """Collect all actions for the matching objects and their
    materials. Each material-action is to be used only once.
    Return set of actions that can be used as input for
    shift_keyframes().

    Keyword arguments:
    namepattern -- name pattern of objects for which the animation-
                   actions are collected. (default: *)

    """
    # NOTE: If a non-matching object has the same material as a
    # matching object, its material keyframes will be shifted!!
    # If you don't want that, make the non-matching object's material
    # unique beforehand.

    # Find matching objects and store in list
    bpy.ops.object.select_all(action='DESELECT')
    objects = [obj for obj in bpy.data.objects
               if fnmatch.fnmatchcase(obj.name, namepattern)]

    # Gather all necessary actions for the objects and their materials,
    # use set() in order to get unique values only,
    # i.e. each animation-action (especially for materials) shall occur only
    # once.
    actions = set()
    for obj in objects:
        print("Object ", obj.name)

        if obj.animation_data is not None:
            action = obj.animation_data.action
            actions.add(action)

        # Loop over materials of this object
        for matslot in obj.material_slots:
            print("Material ", matslot.name)

            if matslot.material.animation_data is not None:
                action = matslot.material.animation_data.action
                actions.add(action)

    return actions


def shift_keyframes(actions=bpy.data.actions, factor=1, frameshift=0,
                    frame_start=0, frame_end=1000000):
    """
    Shift keyframes by given factor or frameshift for given actions
    within given number of frames.
    In details: shift the keyframe_points and their handles.
    Only works properly for fcurves with bezier-shape or poly-curves.
    Fcurve-modifiers are not taken into account.

    Keyword arguments:
    actions --  set or list of actions for which frames shall be
                shifted (default: all actions available)
    frame_start, frame_end -- range of frames for which keyframe_points
                              are shifted
    factor -- stretch keyframe_points in given range by this factor
    frameshift -- add this number to the keyframe_points in given range
    """

    # Loop over all actions and their fcurves,
    # multiply keyframe-positions and handles by given factor
    # and then shift by given frameshift
    for action in actions:
        print("Action ", action.name)

        for fcu in action.fcurves:
            print("  %s  channel %d" % (fcu.data_path, fcu.array_index))

            for keyframe in fcu.keyframe_points:

                if (keyframe.co[0] >= frame_start
                        and keyframe.co[0] <= frame_end):

                    print("    %s" % keyframe.co)  # coordinates x,y

                    keyframe.co[0] = keyframe.co[0]*factor + frameshift
                    keyframe.handle_left[0] = (keyframe.handle_left[0]*factor
                                               + frameshift)
                    keyframe.handle_right[0] = (keyframe.handle_right[0]*factor
                                                + frameshift)

    return


if __name__ == "__main__":

    # Just stretch everything by factor 3
    #shift_keyframes(factor=3)

    # Get actions for specified objects only
    actions = get_actions_for_objects(namepattern='C*')
    #print('Actions: ', actions)

    # Stretch only keyframes for these animation actions
    shift_keyframes(actions=actions, factor=2)

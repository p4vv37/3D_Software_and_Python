# __author__ = 'Paweł Kowalski'
#
# This script was created to demonstrate the use of Python in Autodesk Maya
#
# Copyright (C) Paweł Kowalski
# www.pkowalski.com
# www.behance.net/pkowalski
#
# Open the script from 3D Studio Max Listener with command:
# python.ExecuteFile "path`to`file\main.py"
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#
#

from PySide import QtCore
from PySide import QtGui
from PySide.QtCore import SIGNAL

from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import maya.mel as mel


import os
import time
import math
import random



def frange(start, end, jump):
    while start < end:
        yield start
        start += jump


def set_scale_keys(target, keyframes):
    """
    Function animates the scale of given object by creating the given keyframes.
    Animation is done with a use of AutoKey function of 3Ds Max.
    The AutoKey function can be set with:
    MaxPlus.Animation.SetAnimateButtonState(Bool)

    :param obj:  MaxPlus.INode - Object which scale will be animated
    :param keyframes: Python list - Keyframes that will be created: [[int time, float scale (1 = 100%),] ...]
    :param multiply_by_ticks: Boolean - Set to False if time in list of keyframes is already multiplied by TICKS.
    """

    for keyframe in keyframes:  # For every keyframe from the list of keyframes scale object at proper time
        scale_value = float(keyframe[0])
        cmds.setKeyframe(target, attribute='scaleX', v=scale_value, time=keyframe[1], itt="fast", ott="fast")
        cmds.setKeyframe(target, attribute='scaleY', v=scale_value, time=keyframe[1], itt="fast", ott="fast")
        cmds.setKeyframe(target, attribute='scaleZ', v=scale_value, time=keyframe[1], itt="fast", ott="fast")


def leafs_rotations(number_of_leafs):
    """
    Creates the list of angles of leafs around the palm tree.
    Leafs should be placed more or less evenly around the trunk but appear to be placed randomly.
    The leafs should not be placed too close, because they would overlap.

    :param num: int - Number of leafs
    :return: Python list - List of angles of leafs around the palm tree
    """

    x = -180  # Leafs are placed around the trunk, so the range is 2*pi (360 deg). x = 0, y = 2*pi would also be ok.
    y = 180
    angles = []
    jump = (y - x) / float(number_of_leafs)  # Devide the range by the number of leafs and create an array

    while x < y:
        random.seed()  #
        angles.append(random.uniform(x - (jump / 3.0), x + (jump / 3.0)))  # every leaf is placed +/- (1/3)*interval
        x += jump

    return angles


def set_position_keys(target, keyframes):
    """
    Function animates the position of given object by creating the given keyframes.
    Animation is done with a use of AutoKey function of 3Ds Max.
    The AutoKey function can be set with:
    MaxPlus.Animation.SetAnimateButtonState(Bool)

    :param obj:  MaxPlus.INode - Object which scale will be animated
    :param keyframes: Python list - Keyframes that will be created: [[int time, [float x, float y, float z]], ...]
    """
    for keyframe in keyframes:  # For every keyframe from the list of keyframes scale object at proper time
        cmds.setKeyframe(target, attribute='translateX', v=keyframe[0][0], time=keyframe[1], itt="fast", ott="fast")
        cmds.setKeyframe(target, attribute='translateY', v=keyframe[0][1], time=keyframe[1], itt="fast", ott="fast")
        cmds.setKeyframe(target, attribute='translateZ', v=keyframe[0][2], time=keyframe[1], itt="fast", ott="fast")


def create_object(verts_pos, face_verts):
    """
    Creates a simple mesh of shark fin.
    Function is written in a readable and easy to interpret, but not effective way.
    The mesh is created based on saved positions of verticles and parameters of faces.
    Data has been generated from object modeled in 3Ds Max with a use of obj_to_code.ms script.
    Similar functions can be used in importer plugin.

    :param mesh: MaxPlus.Mesh - The mesh that will be modified
    """

    shark_mesh = om.MObject()
    points = om.MFloatPointArray()

    for vert in verts_pos:  # add every point to Maya float points array
        p = om.MFloatPoint(vert[0], vert[2], -vert[1])
        points.append(p)

    face_connects = om.MIntArray()  # an array for vertice numbers per face
    face_counts = om.MIntArray()  # an array for total number of vertices per face
    for verts in face_verts:
        face_connects.append(verts[0])  # Append vertices of face.
        face_connects.append(verts[1])
        face_connects.append(verts[2])
        face_counts.append(len(verts))  # append the number of vertices for this face
    mesh_fs = om.MFnMesh()
    mesh_fs.create(points, face_counts, face_connects, parent=shark_mesh)
    mesh_fs.updateSurface()
    node_name = mesh_fs.name()
    cmds.polySoftEdge(node_name, a=30, ch=1)

    # assign new mesh to default shading group
    cmds.sets(node_name, e=True, fe='initialShadingGroup')
    return cmds.listRelatives(node_name, fullPath=True, parent=True)


def create_palm(diameter, segs_num, leafs_num, bending, id_num, anim_start, anim_end):
    """
    Function creates a single palm tree.
    This function was created to show how to create basic geometry objects, use instances and use modificators.

    :param diameter: float - inner diameter of pine
    :param segs_num: int - number of segments of the pine
    :param leafs_num: int - number of leafs
    :param bending: float - how much bended the pine is
    :param id: int - ID of the tree
    :param anim_start: int - Starting frame of the tree animation
    :param anim_end: int - Ending frame of the tree animation
    """

    keyframe_interval = (anim_end - anim_start) / (segs_num + 1.0)  # interval of scale keframes of the pine segments

    anim_start /= 25.0  # Convert frames to the internal 3Ds Max time unit.
    anim_end /= 25.0  # Need to convert now, because the number of segments is probably
    keyframe_interval /= 25.0  # grater then the number of frames between the start and the end o the animation of tree

    # list of times of keyframes for the pine
    # and leafs. Equal time intervals.
    keyframe_list = list(frange(start=anim_start, end=anim_end, jump=keyframe_interval))

    keyframe_list.reverse()  # Because the pop() will be used and the first frame should be the smallest number

    source_segment = 'segment_orginal'
    cmds.polyCone(r=diameter/2.0, h=-diameter * 8, n=source_segment, subdivisionsY=5)
    cmds.polyDelFacet(source_segment + '.f[20:79]', source_segment + '.f[81:100]')
    cmds.polyNormal(name=source_segment, normalMode=0)
    bbox = cmds.exactWorldBoundingBox(source_segment)
    bottom = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
    cmds.xform(source_segment, piv=bottom, ws=True)

    segments_tab = []  # A list of all the segments of the tree
    for i in xrange(segs_num):
        cmds.refresh(f=True)
        # Create segments of pine of the palm tree

        current_segment_name = 'Palm_element_' + str(id_num) + '_' + str(i)
        cmds.instance('segment_orginal', n=current_segment_name)  # Create an instance with segment geometry
        cmds.move(diameter * i, current_segment_name, moveY=True, absolute=True)  # Every node should be H higher then last one

        # The nodes at the top of the tree should be smaller then those at the bottom:
        cmds.scale(1.0 - (i / (segs_num * 4.0)), 1.0 - (i / (segs_num * 4.0)), 1, current_segment_name)
        segments_tab.append(current_segment_name)  # Append to the nodes table
        anim_start_frame = keyframe_list.pop()  # Pop one time from the keyframe times list
        set_scale_keys(target=current_segment_name, keyframes=[[0.001, str(anim_start_frame) + 'sec'],
                                                               [1.2, str(anim_start_frame + keyframe_interval) + 'sec'],
                                                               [1,
                                                                str(anim_start_frame + 2 * keyframe_interval) + 'sec']])

    cmds.delete(source_segment)
    for current_segment_name in segments_tab:
        # If the segment is not the first segment of the tree then it should be parented to the previous one.
        try:
            cmds.parent(current_segment_name, root,
                        relative=True)  # if there is not old_segment_node the command will fail
        except:  # If the function failed then this is a first node of the tree and will not have any parent
            #cmds.parent(current_segment_name, 'land', relative=True)
            root = current_segment_name

    # The leaf will be created from saved vertex data in a simmilar way to cloud.

    verts_list = [[0.0874634, 0.283682, -0.150049], [-9.33334, 3.45312, -5.19915], [-0.0979366, -0.242619, -0.151449],
                  [0.0756626, 0.288981, 0.00435066], [-0.110037, -0.237219, 0.00305176],
                  [-0.0341358, 0.0332813, 0.222252], [-0.046236, 0.0384817, 0.376751], [-2.00844, -0.0782185, -0.04245],
                  [-1.49184, 1.38118, -0.0476494], [-1.51604, 1.39538, 0.200851], [-2.03964, -0.0789185, 0.205851],
                  [-1.79314, 0.661982, 0.356852], [-8.51614, 2.95795, -3.08655], [-8.65224, 1.73258, -3.67535],
                  [-7.77134, 3.93545, -3.64315], [-7.89874, 3.98053, -3.41335], [-8.77254, 1.77508, -3.43515],
                  [-8.38964, 2.89923, -3.33135], [-1.81954, 0.668982, 0.60585], [-5.86674, 0.829681, -0.820549],
                  [-5.03134, 3.19562, -0.787249], [-5.10854, 3.23514, -0.531349], [-5.94654, 0.870181, -0.570749],
                  [-5.56024, 2.07138, -0.438848], [-5.63774, 2.11408, -0.182249], [-7.35774, 1.29268, -2.00885],
                  [-6.54364, 3.59313, -1.90675], [-6.65514, 3.64373, -1.65775], [-7.46144, 1.34048, -1.75845],
                  [-7.10164, 2.51205, -1.60085], [-3.83754, 1.37038, 0.50765], [-4.09794, 0.257582, -0.106649],
                  [-3.33404, 2.40815, -0.13835], [-3.38054, 2.42888, 0.109451], [-4.14974, 0.269781, 0.141151],
                  [-3.78934, 1.35658, 0.259151], [-7.21234, 2.56052, -1.34435], [-8.70384, 4.0245, -4.67165],
                  [-9.38574, 2.48178, -4.54065], [-9.16784, 3.28523, -4.39535], [-9.32104, 2.46601, -4.65515],
                  [-8.76504, 4.03897, -4.55925], [-9.10294, 3.26697, -4.51255]]

    faces_list = [[0, 5, 8], [3, 9, 6], [0, 8, 3], [1, 40, 38], [2, 5, 4], [5, 2, 11], [1, 38, 39], [5, 0, 6],
                  [17, 37, 14], [15, 39, 12], [37, 41, 15], [7, 2, 10], [40, 42, 17], [10, 4, 18], [11, 32, 8],
                  [9, 33, 18], [8, 32, 9], [13, 25, 16], [7, 31, 11], [16, 28, 12], [23, 29, 20], [21, 36, 24],
                  [20, 27, 21], [19, 34, 22], [19, 29, 23], [22, 30, 24], [35, 20, 32], [33, 21, 30], [32, 20, 33],
                  [25, 19, 28], [31, 19, 35], [28, 22, 36], [29, 17, 26], [27, 12, 36], [26, 15, 27], [31, 10, 34],
                  [25, 17, 29], [34, 18, 30], [40, 13, 38], [38, 16, 12], [42, 1, 37], [41, 1, 39], [37, 1, 41],
                  [40, 1, 42], [5, 11, 8], [9, 18, 6], [8, 9, 3], [5, 6, 4], [2, 7, 11], [0, 3, 6], [17, 42, 37],
                  [15, 41, 39], [15, 14, 37], [2, 4, 10], [17, 13, 40], [4, 6, 18], [11, 35, 32], [33, 30, 18],
                  [32, 33, 9], [25, 28, 16], [31, 35, 11], [28, 36, 12], [29, 26, 20], [21, 27, 36], [20, 26, 27],
                  [19, 31, 34], [19, 25, 29], [22, 34, 30], [35, 23, 20], [21, 24, 30], [20, 21, 33], [19, 22, 28],
                  [19, 23, 35], [22, 24, 36], [17, 14, 26], [27, 15, 12], [26, 14, 15], [31, 7, 10], [25, 13, 17],
                  [34, 10, 18], [13, 16, 38], [12, 39, 38]]

    leaf_source_name = create_object(verts_list, faces_list)
    cmds.rename(leaf_source_name, "leaf")

    anim_start_frame = keyframe_list.pop()

    last_node = segments_tab[-1]
    for rot_z in leafs_rotations(number_of_leafs=leafs_num):  # Leafs should be distributed around the pine.
        current_leaf_name = "leaf_" + str(id_num) + '_' + str(i)
        cmds.instance("leaf", n=current_leaf_name)
        cmds.move(diameter*4, current_leaf_name, moveY=True, relative=True)

        cmds.rotate(random.uniform(-math.pi / 15, math.pi / 15), rot_z, random.uniform(-math.pi / 8, math.pi / 10),
                    current_leaf_name)  # The rotation can be set with a number of ways. Here, the current rotation is read
        # and modified as Euler. Also, the quaternon can be used with Rotate function.
        set_scale_keys(target=current_leaf_name,
                       keyframes=[[0.001, str(anim_start_frame)+"sec"],
                                  [1, str(anim_start_frame + keyframe_interval)+"sec"]])
        cmds.parent(current_leaf_name, last_node, relative = True)
        cmds.scale(0.9, 0.9, 0.9, current_leaf_name)
        #segments_tab.append(current_leaf_name)
        i += 1

    cmds.delete("leaf")
    cmds.nonLinear(root, type='bend', after = True, curvature=2*bending, lowBound=0)

    for name in cmds.ls():
        if name.endswith('Handle'):
            cmds.scale(60,60,60,name)

    return root


def prepare_scene(path):
    """
    The function sets the basic parameters of the scene: time range, tangent type of keyframes and render settings.

    :param path: string - The directory with necessary files
    """

    cmds.playbackOptions(min=0, max=260)  # Set the animation range

    cmds.autoKeyframe(state=False)  # Make sure, that the AutoKey button is disabled

    # Set the render settings
    # Load Mental ray (will throw an error if exists, use e.g. try-except to get around that)
    #try:
    #    cmds.loadPlugin('Mayatomr', quiet=True)

        # Autoload Mental ray
    #    cmds.pluginInfo('Mayatomr', edit=True, autoload=True)

        # change render drop down
    #    cmds.setAttr('defaultRenderGlobals.ren', 'mentalRay', type='string')
    #except:
    #    pass
    # example on render settings change
    #Change samples
    #cmds.setAttr('miDefaultOptions.maxSamples', 2);

    # Set filter to Mitchell
    #cmds.setAttr('miDefaultOptions.filter', 3);

    #Enable final gather
    #cmds.setAttr('miDefaultOptions.finalGather', 1)

    cam = cmds.camera(name="RenderCamera", focusDistance=35, position=[-224.354, 79.508, 3.569], rotation=[-19.999,-90,0])  # create camera to set its background
    # Set Image Plane for camera background
    cmds.imagePlane(camera=cmds.ls(cam)[1], fileName=(path.replace("\\", "/") + '/bg.bmp'))
    cmds.setAttr("imagePlaneShape1.depth", 400)


def import_and_animate_basic_meshes(path):
    """
    This function imports some objects and animates them.
    It was created to show how to import objects and present one way of creating keyframes of animation.

    :param path: string - The directory with necessary files
    """

    cmds.file(path + '\water.obj', i=True)  # Import an obj file
    set_scale_keys(target="water", keyframes=[[0.001, 1], [1, 9]])  # Set the animation keys

    cmds.file(path + '\land.obj', i=True)
    set_scale_keys(target="land", keyframes=[[0.001, 8], [1, 11]])


def create_shark_and_cloud():
    """
    Creates meshes from vertex and face data.
    Two functions are used: one is easier to read an one is more useful.
    Similar functions can be used in importer plugin.
    """
    shark_verts_pos = [[-2.42281, -0.814631, 1.55561], [0.0166863, -0.854455, 1.91858], [-2.42281, -0.482041, 1.55561],
                       [0.0166863, -0.44221, 1.91858], [-2.57592, -0.814631, 3.45857], [-1.41455, -0.810425, 3.54678],
                       [-2.57592, -0.482041, 3.45857], [-1.41455, -0.486246, 3.54678], [-2.54367, -0.8214, -0.819357],
                       [-2.54367, -0.475272, -0.819357], [0.422536, -0.421143, -0.277747],
                       [0.422536, -0.875526, -0.277747]]
    shark_face_verts = [[8, 10, 11], [4, 7, 6], [0, 5, 4], [1, 7, 5], [3, 6, 7], [2, 4, 6], [0, 9, 8], [2, 10, 9],
                        [3, 11, 10], [1, 8, 11], [8, 9, 10], [4, 5, 7], [0, 1, 5], [1, 3, 7], [3, 2, 6], [2, 0, 4],
                        [0, 2, 9], [2, 3, 10], [3, 1, 11], [1, 0, 8]]

    shark_node_name = create_object(shark_verts_pos, shark_face_verts)
    cmds.rename(shark_node_name, "shark")
    set_scale_keys(target="shark", keyframes=[[0.001, 9], [1, 15]])
    cmds.move(-9.18464, -4, -54.9695, "shark", absolute=True)  # Set position

    cloud_verts_pos = [[-4.59048, -11.5324, -2.85738], [4.19166, -11.3976, -1.66769], [-2.72098, 4.70308, -0.947684],
                       [5.35751, 5.31851, -1.84713], [-2.55545, -10.6202, 1.76613], [6.33762, -11.4932, 3.83193],
                       [-4.05797, 5.18567, 4.01239], [5.16506, 4.23825, 3.03181], [-7.57451, -3.27952, -1.45211],
                       [-5.04695, -3.47346, -2.50455], [0.944433, 6.59175, -3.95915], [5.33078, -2.79647, -1.9336],
                       [-1.41402, -13.436, -1.63148], [2.25454, -13.8944, 4.36555], [5.20539, -3.61147, 4.18473],
                       [1.21982, 6.42224, 2.21349], [-5.31748, -3.30419, 3.23747], [6.47434, -13.4315, 0.369284],
                       [-4.49047, -13.0672, -0.366047], [7.06894, 7.09671, -0.225245], [-3.55781, 7.03288, 2.01675],
                       [-4.64846, -11.0102, -2.8238], [-5.21395, -10.2643, -2.81557], [-5.11732, -9.4053, -2.68607],
                       [-4.63491, -8.46356, -2.67066], [-4.67857, -7.34732, -3.28498], [-4.66886, -6.0801, -2.95555],
                       [-4.96425, -4.77316, -3.20924], [-3.07051, 4.22094, -1.27774], [-3.28412, 3.47717, -1.22602],
                       [-3.06383, 2.42297, -1.70111], [-4.21875, 1.15586, -2.44524], [-4.59185, 0.108139, -1.878],
                       [-4.55174, -1.04221, -2.62517], [-5.07763, -2.24332, -2.5385], [-2.5496, 5.2281, -1.08924],
                       [-2.47412, 5.97114, -1.56816], [-2.32934, 6.64407, -2.13384], [-1.81588, 6.7158, -2.66064],
                       [-1.09603, 6.51815, -3.1696], [-0.384585, 6.59353, -3.55172], [0.2763, 6.63422, -3.91024],
                       [4.97608, 5.33017, -2.21633], [4.42463, 5.3988, -2.82698], [3.87665, 5.59257, -3.30965],
                       [3.39066, 6.12778, -3.09912], [2.87637, 6.75938, -2.90991], [2.28094, 6.88389, -3.07711],
                       [1.62215, 6.6081, -3.54207], [5.6303, 4.88423, -1.69767], [5.93795, 4.18237, -2.02055],
                       [6.34299, 3.28777, -2.50259], [6.01454, 2.16795, -2.41291], [5.48294, 0.915054, -1.48493],
                       [5.56809, -0.331761, -1.62049], [5.22757, -1.57047, -1.65198], [4.34654, -10.8263, -1.71773],
                       [4.03986, -10.0871, -1.25091], [4.44435, -9.26752, -1.48684], [4.98975, -8.10985, -2.09718],
                       [5.97541, -6.66577, -2.29159], [6.40411, -5.31424, -1.4463], [5.74385, -4.03539, -2.07227],
                       [3.67823, -11.9509, -1.39023], [2.99699, -12.6519, -1.24017], [2.34207, -12.9799, -1.36114],
                       [1.56308, -12.9821, -1.2517], [0.805849, -13.3548, -0.833223], [0.0592078, -13.9428, -0.927655],
                       [-0.69599, -13.9633, -1.40722], [-4.48329, -11.8284, -3.03768], [-4.25605, -12.4004, -3.18883],
                       [-3.80349, -12.8516, -3.39871], [-3.33853, -12.9033, -3.36947], [-2.8886, -12.6499, -2.84013],
                       [-2.44545, -12.7983, -2.31099], [-1.98028, -12.9664, -1.95086], [-2.35827, -11.0242, 1.95376],
                       [-2.04212, -11.8418, 2.40821], [-1.43451, -12.5864, 2.6025], [-0.464936, -12.8909, 2.70888],
                       [0.277662, -13.0811, 3.36934], [0.744878, -13.5168, 3.99864], [1.39473, -13.9213, 4.33037],
                       [5.84659, -11.8736, 4.11287], [5.35056, -12.4986, 4.28095], [4.93181, -13.3184, 4.37555],
                       [4.62338, -14.1254, 4.68631], [4.25795, -14.4315, 4.95028], [3.74167, -14.2483, 4.93854],
                       [3.06639, -13.9383, 4.62452], [6.93981, -10.9459, 3.54401], [6.81082, -10.1381, 3.49907],
                       [5.67307, -9.16372, 4.27475], [5.07461, -8.06029, 4.44253], [5.59865, -6.89624, 3.44476],
                       [5.71477, -5.76001, 4.10377], [5.43378, -4.68175, 4.73674], [5.26349, 3.76686, 2.83477],
                       [5.03478, 3.10254, 2.51034], [5.60882, 2.3842, 2.96899], [5.28509, 1.44248, 4.19756],
                       [5.06031, 0.227875, 4.11658], [5.74926, -1.10308, 4.13182], [5.23316, -2.41592, 4.08796],
                       [4.77104, 4.2432, 2.87455], [4.26316, 4.37717, 2.64462], [3.77346, 4.88327, 2.60995],
                       [3.33051, 5.59131, 2.87838], [2.8952, 5.78294, 3.20531], [2.40009, 5.74118, 3.04044],
                       [1.83982, 6.00027, 2.49207], [-3.6252, 5.55577, 4.01007], [-3.01992, 5.85201, 3.70423],
                       [-2.42564, 5.92598, 3.42756], [-1.77262, 6.08702, 3.08948], [-1.00918, 6.32267, 2.76293],
                       [-0.205574, 6.30027, 2.54408], [0.543592, 6.39312, 2.26653], [-4.3646, 4.48682, 3.61868],
                       [-4.17321, 3.39143, 3.43435], [-4.33876, 2.23708, 3.90402], [-4.28137, 1.23009, 3.54935],
                       [-5.12764, 0.0918598, 3.99807], [-5.19081, -1.02315, 3.43132], [-5.29362, -2.11191, 2.91219],
                       [-2.60726, -10.127, 2.17327], [-3.51078, -9.45301, 2.9977], [-3.79006, -8.71694, 3.36178],
                       [-4.10539, -7.95529, 2.76918], [-4.42019, -6.85349, 2.78951], [-4.84402, -5.52935, 2.81615],
                       [-5.09285, -4.46128, 3.52657], [4.30574, -11.5671, -1.50565], [4.50195, -11.8334, -1.25188],
                       [4.83568, -12.1377, -0.98148], [5.20644, -12.408, -0.722621], [5.55156, -12.5921, -0.461673],
                       [5.89193, -12.7367, -0.20753], [6.24181, -12.9731, 0.0607195], [6.29933, -11.7357, 3.70063],
                       [6.30325, -12.1743, 3.31666], [6.22233, -12.6801, 2.81164], [5.95056, -13.1009, 2.2757],
                       [5.81332, -13.7173, 1.74536], [6.03473, -14.0856, 1.23336], [6.39401, -13.9265, 0.764305],
                       [-3.11063, -10.9355, 1.50183], [-3.75236, -11.6171, 1.07977], [-4.00088, -12.4831, 0.713789],
                       [-3.78955, -13.2201, 0.516292], [-3.5181, -13.5544, 0.376321], [-3.54252, -13.4297, 0.189794],
                       [-3.90938, -13.1606, -0.068965], [-4.75366, -11.8561, -2.68642], [-4.89771, -12.3524, -2.40486],
                       [-5.09703, -12.9067, -2.14409], [-5.40772, -13.3663, -1.91872], [-5.6412, -13.5851, -1.59908],
                       [-5.5659, -13.5145, -1.1818], [-5.09332, -13.2428, -0.743286], [5.45017, 5.73622, -1.85555],
                       [5.63365, 6.26245, -1.85505], [6.1073, 6.76594, -1.94462], [6.58044, 7.20559, -1.85469],
                       [6.88931, 7.53961, -1.51406], [7.10716, 7.66078, -1.04544], [7.19471, 7.51389, -0.59239],
                       [5.40772, 4.66524, 3.02514], [5.76931, 5.01291, 2.65931], [6.14507, 5.2088, 2.16144],
                       [6.27824, 5.38063, 1.43376], [6.17431, 5.62542, 0.759444], [6.24094, 5.98304, 0.33088],
                       [6.67544, 6.4994, 0.0532598], [-2.6477, 4.65851, -0.662931], [-2.71723, 4.72583, -0.337669],
                       [-3.02974, 5.03001, 0.0133729], [-3.55156, 5.4128, 0.457088], [-4.08555, 5.6588, 0.878288],
                       [-4.20689, 6.06137, 1.27083], [-3.94135, 6.61804, 1.64613], [-3.90152, 5.41826, 3.96519],
                       [-3.68639, 5.69672, 3.7975], [-3.57372, 5.96746, 3.6043], [-3.50975, 6.24396, 3.36952],
                       [-3.38908, 6.56161, 3.08272], [-3.23099, 6.92618, 2.74989], [-3.27483, 7.14141, 2.38829],
                       [1.45619, -7.49005, -3.83906], [-2.15714, 3.22855, 4.74324], [-3.20732, -16.3363, 0.593722],
                       [8.50918, 6.1379, -0.126037], [-1.3075, 10.5179, 0.0826635], [6.66269, -11.5952, 0.976294],
                       [6.18407, -10.885, 3.95382], [4.6369, -16.5258, 3.13471], [-6.47456, -10.6289, -2.18081],
                       [-2.82653, 6.85526, 3.372], [-2.65245, 4.26594, -0.23955], [6.45967, -11.2423, 3.81836],
                       [1.33039, -11.5956, 4.72251], [1.30475, 4.5572, -3.30185], [8.00107, -6.69582, 2.12858],
                       [4.57166, 6.984, 2.49627], [-3.24572, -12.1366, -3.56982], [5.3204, 6.36013, -2.56745],
                       [-3.11957, 7.73189, 2.69959], [6.77177, 0.0625889, 4.49272], [6.94192, -4.53513, -1.62334],
                       [7.13623, 2.29023, 2.48835], [-5.82156, -11.0413, 0.905474], [-1.63365, -0.816481, -2.63599],
                       [-3.79753, -3.1284, 4.1384], [-6.72222, 2.34786, 1.69348], [-0.365939, -17.3946, 3.7759],
                       [-2.86998, 8.92864, -2.32206], [-1.19507, -7.54906, -2.6852], [4.65156, 2.46804, -4.03467],
                       [3.35007, -14.7047, 0.201495], [1.6206, 3.8501, 3.19007], [2.27385, 10.1786, 0.636264],
                       [-0.511457, -9.4981, 5.60078], [1.90472, -3.64936, 4.72947], [-3.64124, -14.7226, 1.98156],
                       [0.714248, -11.7933, -1.52495], [-7.27783, -2.97639, 1.02711], [0.0551114, -15.631, 0.740704],
                       [4.08346, -6.60669, 4.23111], [-3.96676, -3.6568, -3.18453], [0.128981, -15.0967, 4.90768],
                       [5.1814, -0.697958, -2.3693], [-2.24666, 3.46083, -1.55516], [-1.03731, 9.80536, -2.4258],
                       [2.76201, 7.5254, -2.57689], [-3.21442, 0.849207, -3.77201], [-4.5522, 4.79028, 3.52668],
                       [-4.2064, -13.7668, -2.8477], [7.41965, 0.205489, 0.882005], [-7.04821, -1.17492, -1.75941],
                       [7.28529, -10.4271, 2.98472], [7.00561, -4.39045, 2.97423], [2.43302, 1.91306, 4.44534],
                       [2.09039, -17.1687, 0.520695], [-3.27282, 1.6396, 3.67241], [-6.87723, -7.81655, 0.412325],
                       [5.25677, 8.8326, 0.858971], [-1.28577, -11.2257, 2.07694], [0.805838, 8.11066, 0.90506],
                       [-0.46974, -2.74816, 4.81187], [-3.06642, 7.51852, -0.246379], [4.55288, 2.79781, 2.29269],
                       [4.04536, -8.45291, -2.82363], [-1.69131, -8.69729, 4.54945], [7.44942, 3.06384, -0.812776],
                       [-0.375084, 2.10788, -3.87666], [-2.33075, -13.1125, 1.34638], [3.73976, -15.1661, 5.22367],
                       [-4.13958, -10.4225, 1.48909], [-6.57359, -4.40388, -2.5274], [-1.19156, -17.5279, 2.70367],
                       [1.48849, 0.940755, -3.11198], [-6.25666, -8.51528, -2.26368], [5.42219, -14.6917, 0.904344],
                       [-5.30033, 2.91069, 2.77322], [-3.69181, 5.1199, 4.16583], [5.23465, -10.0999, -0.279651],
                       [3.30916, -9.50085, 4.15144], [6.64312, -7.95079, 0.064867], [2.06641, -11.3195, -2.02518],
                       [-6.87761, -1.18354, 1.26735], [-1.93959, -3.56711, -3.96444], [-0.33943, -13.7318, 2.4941],
                       [3.44558, -13.2893, 5.10556], [-3.73378, -8.56427, -2.31567], [-2.35109, -5.13952, 5.32983],
                       [6.42324, 0.543804, 2.58669], [7.86166, -5.16509, 0.692536], [3.76085, -3.61315, -3.37012],
                       [5.44298, -14.2463, 3.15755], [-1.70985, -15.7899, 0.0519905], [2.26734, -13.5848, -1.39097],
                       [5.74778, 6.39146, 1.10414], [-2.11671, 9.79717, 1.08835], [2.8608, 8.25119, 1.23121],
                       [-1.18382, 4.3518, 3.89946], [7.96713, 5.05793, 1.41253], [-6.69457, -4.65279, -1.21029],
                       [0.0191634, -9.11299, -2.26856], [-3.81062, -7.07655, 2.93881], [-7.32947, 0.0447152, 1.78407],
                       [1.69836, -8.23934, 4.66153], [-6.6485, -10.8634, -0.11143], [-4.06035, -15.9321, 1.42343],
                       [4.5849, 7.70502, -0.677262], [-1.09886, -1.13732, 5.43579], [2.70622, -0.301464, -3.82059],
                       [-5.6857, -1.744, -2.71823], [-5.81655, -12.8909, -1.16874], [0.289658, -18.1278, 2.42564],
                       [-4.47469, -6.57199, 2.10047], [0.112202, 10.0015, 0.627223], [0.235416, 8.04662, -3.31171],
                       [-2.24934, -5.91415, -2.4902], [-2.55157, 4.50158, -2.19153], [6.43219, 3.07829, 2.6692],
                       [-3.97414, 5.64061, 1.87932], [-4.56586, 0.0207524, 4.42228], [4.63573, -2.79558, 3.89731],
                       [6.43056, -6.98187, 3.0528], [-0.986888, -5.57974, 4.56781], [2.21565, 4.82825, 3.77766],
                       [-1.71112, -11.9039, -1.80275], [2.9143, -7.33767, -3.12538], [3.40413, -13.6728, -0.739559],
                       [7.51963, -2.20202, 0.395068], [5.59617, -12.9598, 1.13681], [-2.42802, 6.61584, -0.938049],
                       [5.51021, -11.3324, -0.968232], [6.25447, 5.61217, -1.3508], [-1.20197, 8.31877, -2.62206],
                       [4.7415, 1.08838, 4.32509], [5.97589, -3.48225, -1.75155], [-2.15625, -15.757, 0.921245],
                       [-2.94145, -6.93029, -3.58556], [2.64081, 5.92833, -2.84607], [3.95925, -17.4688, 1.86022],
                       [-3.52455, -14.873, 0.832899], [-3.21377, -9.36567, 4.09077], [-4.48335, -7.68947, 1.74946]]

    cloud_face_verts = [[0, 21, 205], [205, 70, 0], [21, 22, 205], [22, 23, 205], [23, 24, 274], [24, 25, 324],
                        [25, 26, 229], [26, 27, 229], [27, 9, 229], [205, 71, 70], [205, 72, 71], [205, 73, 72],
                        [205, 74, 73], [312, 75, 74], [312, 76, 75], [312, 12, 76], [28, 2, 35], [35, 304, 28],
                        [304, 35, 36], [304, 36, 37], [304, 37, 38], [304, 38, 39], [232, 39, 40], [232, 40, 41],
                        [202, 41, 10], [29, 28, 304], [30, 29, 304], [31, 30, 232], [32, 31, 235], [33, 32, 235],
                        [34, 33, 235], [9, 34, 229], [3, 49, 218], [218, 42, 3], [49, 50, 218], [50, 51, 218],
                        [51, 52, 218], [52, 53, 261], [53, 54, 231], [54, 55, 231], [55, 11, 278], [218, 43, 42],
                        [218, 44, 43], [325, 45, 44], [325, 46, 45], [325, 47, 46], [325, 48, 47], [202, 10, 48],
                        [56, 1, 63], [63, 269, 56], [269, 63, 64], [269, 64, 65], [269, 65, 66], [269, 66, 67],
                        [225, 67, 68], [225, 68, 69], [312, 69, 12], [57, 56, 269], [58, 57, 269], [59, 58, 269],
                        [60, 59, 252], [61, 60, 252], [62, 61, 313], [11, 62, 278], [4, 77, 247], [247, 126, 4],
                        [77, 78, 247], [78, 79, 247], [79, 80, 247], [80, 81, 201], [81, 82, 201], [82, 83, 201],
                        [83, 13, 201], [247, 127, 126], [328, 128, 127], [289, 129, 128], [289, 130, 129],
                        [275, 131, 130], [275, 132, 131], [213, 16, 132], [84, 5, 91], [91, 200, 84], [200, 91, 92],
                        [195, 92, 93], [273, 93, 94], [267, 94, 95], [267, 95, 96], [228, 96, 97], [228, 97, 14],
                        [85, 84, 200], [86, 85, 195], [87, 86, 195], [88, 87, 195], [89, 88, 273], [90, 89, 273],
                        [13, 90, 273], [7, 105, 251], [251, 98, 7], [105, 106, 251], [106, 107, 311], [107, 108, 311],
                        [108, 109, 311], [109, 110, 311], [110, 111, 285], [111, 15, 285], [251, 99, 98],
                        [251, 100, 99], [321, 101, 100], [321, 102, 101], [223, 103, 102], [308, 104, 103],
                        [308, 14, 104], [112, 6, 119], [119, 265, 112], [265, 119, 120], [265, 120, 121],
                        [190, 121, 122], [244, 122, 123], [307, 123, 124], [307, 124, 125], [213, 125, 16],
                        [113, 112, 265], [114, 113, 265], [115, 114, 265], [116, 115, 285], [117, 116, 285],
                        [118, 117, 285], [15, 118, 285], [0, 70, 237], [237, 154, 0], [70, 71, 237], [71, 72, 237],
                        [72, 73, 280], [73, 74, 280], [74, 75, 280], [75, 76, 227], [76, 12, 227], [237, 155, 154],
                        [237, 156, 155], [237, 157, 156], [237, 158, 157], [327, 159, 158], [327, 160, 159],
                        [327, 18, 160], [63, 1, 133], [133, 314, 63], [314, 133, 134], [314, 134, 135], [314, 135, 136],
                        [314, 136, 137], [314, 137, 138], [263, 138, 139], [263, 139, 17], [64, 63, 314], [65, 64, 281],
                        [66, 65, 281], [67, 66, 281], [68, 67, 219], [69, 68, 227], [12, 69, 227], [5, 84, 279],
                        [279, 140, 5], [84, 85, 279], [85, 86, 279], [86, 87, 279], [87, 88, 257], [88, 89, 257],
                        [89, 90, 230], [90, 13, 230], [279, 141, 140], [279, 142, 141], [279, 143, 142],
                        [263, 144, 143], [263, 145, 144], [263, 146, 145], [263, 17, 146], [77, 4, 147], [147, 256, 77],
                        [256, 147, 148], [256, 148, 149], [256, 149, 150], [256, 150, 151], [327, 151, 152],
                        [327, 152, 153], [327, 153, 18], [78, 77, 256], [79, 78, 256], [80, 79, 272], [81, 80, 272],
                        [82, 81, 272], [83, 82, 230], [13, 83, 230], [1, 56, 318], [318, 133, 1], [56, 57, 266],
                        [57, 58, 266], [58, 59, 209], [59, 60, 209], [60, 61, 209], [61, 62, 322], [62, 11, 322],
                        [318, 134, 133], [318, 135, 134], [318, 136, 135], [318, 137, 136], [318, 138, 137],
                        [318, 139, 138], [316, 17, 139], [49, 3, 161], [161, 319, 49], [319, 161, 162], [319, 162, 163],
                        [319, 163, 164], [319, 164, 165], [192, 165, 166], [192, 166, 167], [192, 167, 19],
                        [50, 49, 319], [51, 50, 319], [52, 51, 254], [53, 52, 254], [54, 53, 254], [55, 54, 238],
                        [11, 55, 238], [7, 98, 305], [305, 168, 7], [98, 99, 305], [99, 100, 305], [100, 101, 208],
                        [101, 102, 208], [102, 103, 208], [103, 104, 208], [104, 14, 241], [305, 169, 168],
                        [305, 170, 169], [286, 171, 170], [286, 172, 171], [286, 173, 172], [192, 174, 173],
                        [192, 19, 174], [91, 5, 140], [140, 240, 91], [240, 140, 141], [240, 141, 142], [240, 142, 143],
                        [240, 143, 144], [316, 144, 145], [316, 145, 146], [316, 146, 17], [92, 91, 240], [93, 92, 240],
                        [94, 93, 240], [95, 94, 309], [96, 95, 309], [97, 96, 241], [14, 97, 241], [3, 42, 206],
                        [206, 161, 3], [42, 43, 206], [43, 44, 206], [44, 45, 234], [45, 46, 234], [46, 47, 234],
                        [47, 48, 302], [48, 10, 302], [206, 162, 161], [206, 163, 162], [206, 164, 163],
                        [206, 165, 164], [246, 166, 165], [246, 167, 166], [204, 19, 167], [35, 2, 175], [175, 317, 35],
                        [317, 175, 176], [317, 176, 177], [317, 177, 178], [317, 178, 179], [250, 179, 180],
                        [250, 180, 181], [250, 181, 20], [36, 35, 317], [37, 36, 317], [38, 37, 317], [39, 38, 320],
                        [40, 39, 320], [41, 40, 320], [10, 41, 320], [6, 112, 198], [198, 182, 6], [112, 113, 198],
                        [113, 114, 198], [114, 115, 248], [115, 116, 248], [116, 117, 248], [117, 118, 248],
                        [118, 15, 284], [198, 183, 182], [198, 184, 183], [207, 185, 184], [207, 186, 185],
                        [207, 187, 186], [207, 188, 187], [250, 20, 188], [105, 7, 168], [168, 282, 105],
                        [282, 168, 169], [282, 169, 170], [282, 170, 171], [282, 171, 172], [282, 172, 173],
                        [282, 173, 174], [204, 174, 19], [106, 105, 282], [107, 106, 282], [108, 107, 282],
                        [109, 108, 204], [110, 109, 204], [111, 110, 284], [15, 111, 284], [2, 28, 199], [199, 175, 2],
                        [28, 29, 199], [29, 30, 199], [30, 31, 239], [31, 32, 239], [32, 33, 297], [33, 34, 297],
                        [34, 9, 259], [199, 176, 175], [199, 177, 176], [199, 178, 177], [199, 179, 178],
                        [306, 180, 179], [306, 181, 180], [306, 20, 181], [21, 0, 154], [154, 298, 21], [298, 154, 155],
                        [298, 155, 156], [298, 156, 157], [298, 157, 158], [298, 158, 159], [298, 159, 160],
                        [211, 160, 18], [22, 21, 298], [23, 22, 197], [24, 23, 197], [25, 24, 197], [26, 25, 262],
                        [27, 26, 262], [9, 27, 259], [4, 126, 258], [258, 147, 4], [126, 127, 258], [127, 128, 329],
                        [128, 129, 329], [129, 130, 300], [130, 131, 300], [131, 132, 226], [132, 16, 270],
                        [258, 148, 147], [211, 149, 148], [211, 150, 149], [211, 151, 150], [211, 152, 151],
                        [211, 153, 152], [211, 18, 153], [119, 6, 182], [182, 236, 119], [236, 182, 183],
                        [236, 183, 184], [236, 184, 185], [236, 185, 186], [236, 186, 187], [236, 187, 188],
                        [306, 188, 20], [120, 119, 236], [121, 120, 264], [122, 121, 264], [123, 122, 264],
                        [124, 123, 290], [125, 124, 290], [16, 125, 270], [240, 309, 94], [209, 266, 58],
                        [93, 273, 195], [195, 273, 88], [219, 227, 68], [230, 257, 89], [300, 329, 129], [262, 259, 27],
                        [184, 198, 207], [248, 198, 114], [239, 199, 30], [179, 199, 306], [200, 195, 85],
                        [92, 195, 200], [130, 289, 275], [14, 308, 228], [278, 231, 55], [232, 235, 31],
                        [208, 305, 100], [194, 268, 203], [167, 246, 204], [204, 284, 110], [274, 205, 23],
                        [74, 205, 312], [234, 206, 44], [165, 206, 246], [207, 198, 283], [188, 207, 250],
                        [276, 241, 315], [241, 208, 104], [238, 322, 11], [315, 241, 322], [170, 305, 286],
                        [254, 238, 54], [160, 211, 298], [259, 262, 245], [235, 229, 34], [255, 296, 271],
                        [102, 321, 223], [125, 213, 307], [239, 214, 199], [290, 270, 125], [256, 272, 79],
                        [243, 299, 227], [302, 234, 47], [207, 283, 250], [288, 225, 205], [296, 189, 217],
                        [202, 261, 255], [44, 218, 325], [143, 279, 263], [299, 243, 326], [285, 311, 110],
                        [220, 285, 249], [301, 221, 302], [284, 248, 118], [223, 222, 291], [127, 247, 328],
                        [295, 244, 213], [310, 222, 223], [158, 237, 327], [224, 323, 230], [225, 288, 313],
                        [269, 252, 59], [287, 245, 300], [214, 239, 270], [323, 280, 260], [280, 237, 72],
                        [94, 267, 273], [291, 222, 201], [229, 324, 25], [217, 271, 296], [215, 257, 230],
                        [215, 230, 323], [261, 218, 52], [261, 202, 218], [41, 202, 232], [255, 232, 202],
                        [233, 216, 193], [320, 302, 10], [294, 234, 302], [234, 294, 206], [235, 232, 255],
                        [229, 235, 212], [214, 306, 199], [236, 264, 120], [280, 191, 237], [293, 327, 237],
                        [210, 276, 238], [238, 254, 210], [259, 297, 34], [8, 270, 239], [144, 316, 240],
                        [194, 203, 240], [309, 241, 96], [277, 322, 241], [242, 220, 249], [311, 251, 106],
                        [243, 219, 196], [219, 243, 227], [190, 244, 295], [122, 244, 190], [329, 300, 245],
                        [292, 245, 262], [284, 204, 246], [294, 302, 221], [201, 247, 80], [247, 201, 222],
                        [221, 301, 248], [198, 248, 283], [223, 249, 310], [321, 249, 223], [317, 320, 38],
                        [250, 193, 216], [100, 251, 321], [251, 220, 242], [189, 313, 288], [313, 278, 62],
                        [222, 253, 247], [222, 275, 253], [319, 254, 51], [286, 210, 254], [255, 212, 235],
                        [271, 212, 255], [256, 224, 272], [151, 327, 256], [257, 279, 87], [196, 257, 299],
                        [148, 258, 211], [245, 292, 329], [239, 259, 8], [245, 287, 259], [215, 299, 257],
                        [215, 323, 260], [189, 296, 231], [231, 261, 53], [197, 292, 262], [197, 262, 25],
                        [263, 196, 219], [138, 263, 314], [264, 290, 123], [306, 214, 264], [121, 190, 265],
                        [265, 285, 115], [266, 268, 194], [139, 318, 316], [291, 228, 223], [96, 228, 267],
                        [277, 268, 209], [266, 209, 268], [67, 225, 269], [313, 269, 225], [270, 8, 226],
                        [270, 226, 132], [271, 217, 303], [212, 271, 229], [272, 230, 82], [230, 272, 224],
                        [273, 201, 13], [201, 273, 291], [324, 274, 24], [217, 205, 274], [132, 275, 213],
                        [213, 310, 249], [241, 276, 208], [210, 208, 276], [241, 309, 277], [268, 277, 203],
                        [231, 278, 189], [278, 313, 189], [196, 263, 279], [279, 257, 196], [280, 227, 299],
                        [227, 280, 75], [281, 219, 67], [314, 281, 64], [174, 204, 282], [282, 204, 108],
                        [283, 248, 193], [193, 250, 283], [248, 284, 221], [246, 221, 284], [190, 249, 285],
                        [285, 265, 190], [192, 286, 254], [173, 286, 192], [287, 226, 8], [287, 8, 259],
                        [288, 217, 189], [205, 217, 288], [128, 328, 289], [289, 253, 275], [290, 214, 270],
                        [264, 214, 290], [291, 267, 228], [267, 291, 273], [211, 292, 197], [292, 211, 258],
                        [323, 224, 293], [237, 191, 293], [206, 294, 246], [221, 246, 294], [249, 190, 295],
                        [213, 249, 295], [261, 231, 296], [261, 296, 255], [297, 239, 32], [259, 239, 297],
                        [298, 211, 197], [298, 197, 22], [280, 299, 260], [260, 299, 215], [226, 287, 300],
                        [226, 300, 131], [301, 193, 248], [301, 233, 193], [302, 233, 301], [302, 320, 233],
                        [324, 229, 303], [303, 229, 271], [39, 232, 304], [304, 232, 30], [210, 286, 305],
                        [305, 208, 210], [188, 306, 236], [236, 306, 264], [244, 307, 213], [123, 307, 244],
                        [103, 223, 308], [308, 223, 228], [240, 203, 309], [203, 277, 309], [275, 222, 310],
                        [275, 310, 213], [220, 251, 311], [311, 285, 220], [69, 312, 225], [312, 205, 225],
                        [252, 313, 61], [252, 269, 313], [219, 314, 263], [314, 219, 281], [315, 238, 276],
                        [315, 322, 238], [194, 316, 318], [316, 194, 240], [216, 317, 250], [179, 250, 317],
                        [266, 318, 56], [194, 318, 266], [254, 319, 192], [165, 192, 319], [320, 216, 233],
                        [317, 216, 320], [249, 321, 242], [242, 321, 251], [322, 277, 209], [322, 209, 61],
                        [323, 293, 191], [280, 323, 191], [303, 217, 324], [274, 324, 217], [325, 218, 202],
                        [48, 325, 202], [196, 299, 326], [196, 326, 243], [327, 293, 224], [327, 224, 256],
                        [253, 328, 247], [289, 328, 253], [329, 258, 127], [258, 329, 292]]

    cloud_node_name = create_object(cloud_verts_pos, cloud_face_verts)
    cmds.rename(cloud_node_name, "cloud")
    set_scale_keys(target="cloud", keyframes=[[0.001, 62], [1.1, 67], [1, 69]])
    cmds.move(-9.18464, 31, 39.500, "cloud", absolute=True)
    set_position_keys(target="cloud", keyframes=[[[2.409, 31.7, 39.500], 69, [5, 5]],
                                                 [[2.409, 33, 39.500], 97, [5, 5]],
                                                 [[2.409, 32.3, 39.500], 125, [5, 5]],
                                                 [[2.409, 31.5, 39.500], 173, [5, 5]],
                                                 [[2.409, 32.3, 39.500], 220, [5, 5]],
                                                 [[2.409, 31.4, 39.500], 240, [5, 5]]])


def create_chest():
    """
    Function creates an object with a use of macro recorded frm 3Ds max.
    This function shows how to use macros. Macros are actions recorded with a MaxScript Listener and they can be
    evaluated as MaxScripts. Macros are a very simple way of creating simple scripts.
    """
    recorded_macro = '''

CreatePolygonCube;
polyCube -w 1 -h 1 -d 1 -sx 1 -sy 1 -sz 1 -ax 0 1 0 -cuv 4 -ch 1;
// Result: pCube1 polyCube1 //
setAttr "polyCube1.width" 35;
setAttr "polyCube1.height" 25;
setAttr "polyCube1.depth" 60;
setAttr "polyCube1.width" 60;
setAttr "polyCube1.depth" 35;
move -r 0 12.426176 0 ;
move -r 0 -16.909006 0 ;
// Undo: move -r 0 -16.909006 0  //
select -r pCube1 ;
select -r pCube1 ;
move -r 0 12.198762 0 ;
select -r pCube1.f[0:2] pCube1.f[4:5] ;
select -d pCube1.f[0] pCube1.f[2:5] ;
hilite pCube1.f[1] ;
selectMode -component ;
select -r pCube1.f[1] ;
polyExtrudeFacet -constructionHistory 1 -keepFacesTogether 1 -pvx 0 -pvy 24.69876187 -pvz 0 -divisions 1 -twist 0 -taper 1 -off 0.31 -thickness 0 -smoothingAngle 30 pCube1.f[1];
// Result: polyExtrudeFace1 //
move -r 0 3.039953 0 ;
select -r pCube1.f[1] ;
polyExtrudeFacet -constructionHistory 1 -keepFacesTogether 1 -pvx 0 -pvy 27.7387132 -pvz 0 -divisions 1 -twist 0 -taper 1 -off 0.31 -thickness 0 -smoothingAngle 30 pCube1.f[1];
// Result: polyExtrudeFace2 //
move -r 0 3.554939 0 ;
scale -r -p 0cm 31.293651cm 0cm 1 1 0.919502 ;
select -r pCube1.f[1] ;
polyExtrudeFacet -constructionHistory 1 -keepFacesTogether 1 -pvx 0 -pvy 31.29365056 -pvz 0 -divisions 1 -twist 0 -taper 1 -off 0.31 -thickness 0 -smoothingAngle 30 pCube1.f[1];
// Result: polyExtrudeFace3 //
move -r 0 2.96881 0 ;
scale -r -p 0cm 34.262464cm 0cm 1 1 0.820697 ;
select -r pCube1.f[1] ;
polyExtrudeFacet -constructionHistory 1 -keepFacesTogether 1 -pvx 0 -pvy 34.2624635 -pvz 0 -divisions 1 -twist 0 -taper 1 -off 0.31 -thickness 0 -smoothingAngle 30 pCube1.f[1];
// Result: polyExtrudeFace4 //
move -r 0 1.7812 0 ;
scale -r -p 0cm 36.043664cm 0cm 1 1 0.779804 ;
scale -r -p 0cm 36.043664cm 0cm 1 1 0.976608 ;
select -r pCube1.f[1] ;
polyExtrudeFacet -constructionHistory 1 -keepFacesTogether 1 -pvx 0 -pvy 36.04366391 -pvz 0 -divisions 1 -twist 0 -taper 1 -off 0.31 -thickness 0 -smoothingAngle 30 pCube1.f[1];
// Result: polyExtrudeFace5 //
move -r 0 2.138578 0 ;
scale -r -p 0cm 38.182242cm 0cm 1 1 0.333583 ;
select -r pCube1.f[1] ;
//
//
//
polyCube -w 1 -h 1 -d 1 -sx 1 -sy 1 -sz 1 -ax 0 1 0 -cuv 4 -ch 1;
// Result: pCube1 polyCube1 //
hilite pCube1.f[1] ;
hilite -r pCube1 ;
select -r pCube1.e[4:5] pCube1.e[8:9] ;
select -r pCube1.e[4:5] pCube1.e[8:9] ;
polySplitRing -ch on -splitType 2 -divisions 2 -useEqualMultiplier 1 -smoothingAngle 30 -fixQuads 1 ;
// Result: polySplitRing1 //
select -r pCube1.e[0:3] pCube1.e[14] pCube1.e[18] pCube1.e[22] pCube1.e[26] pCube1.e[30] pCube1.e[34] pCube1.e[38] pCube1.e[42] pCube1.e[46] pCube1.e[50] pCube1.e[56] pCube1.e[59] pCube1.e[64] pCube1.e[67] ;
select -r pCube1.e[0:3] pCube1.e[14] pCube1.e[18] pCube1.e[22] pCube1.e[26] pCube1.e[30] pCube1.e[34] pCube1.e[38] pCube1.e[42] pCube1.e[46] pCube1.e[50] pCube1.e[56] pCube1.e[59] pCube1.e[64] pCube1.e[67] ;
polySplitRing -ch on -splitType 2 -divisions 2 -useEqualMultiplier 1 -smoothingAngle 30 -fixQuads 1 ;
// Result: polySplitRing2 //
scale -r -p -2.38419e-006cm 18.940502cm 0cm 1.710318 1 1 ;
//
//
//
select -r pCube1.e[71] ;
select -r pCube1.e[54] pCube1.e[56] pCube1.e[58:59] pCube1.e[71] pCube1.e[97] pCube1.e[107] pCube1.e[133] ;
select -tgl pCube1.e[69] ;
select -r pCube1.e[54] pCube1.e[56] pCube1.e[58:59] pCube1.e[62] pCube1.e[64] pCube1.e[66:67] pCube1.e[69] pCube1.e[71] pCube1.e[97] pCube1.e[99] pCube1.e[105] pCube1.e[107] pCube1.e[133] pCube1.e[135] ;
select -tgl pCube1.e[74] ;
select -r pCube1.e[54] pCube1.e[56] pCube1.e[58:59] pCube1.e[62] pCube1.e[64] pCube1.e[66:67] pCube1.e[69:72] pCube1.e[74] pCube1.e[76] pCube1.e[78] pCube1.e[80] pCube1.e[82] pCube1.e[84] pCube1.e[86] pCube1.e[88] pCube1.e[90] pCube1.e[92] pCube1.e[94] pCube1.e[96:100] pCube1.e[102:103] pCube1.e[105] pCube1.e[107] pCube1.e[133] pCube1.e[135] ;
select -tgl pCube1.e[110] ;
select -r pCube1.e[54] pCube1.e[56] pCube1.e[58:59] pCube1.e[62] pCube1.e[64] pCube1.e[66:67] pCube1.e[69:72] pCube1.e[74] pCube1.e[76] pCube1.e[78] pCube1.e[80] pCube1.e[82] pCube1.e[84] pCube1.e[86] pCube1.e[88] pCube1.e[90] pCube1.e[92] pCube1.e[94] pCube1.e[96:100] pCube1.e[102:103] pCube1.e[105:108] pCube1.e[110] pCube1.e[112] pCube1.e[114] pCube1.e[116] pCube1.e[118] pCube1.e[120] pCube1.e[122] pCube1.e[124] pCube1.e[126] pCube1.e[128] pCube1.e[130] pCube1.e[132:136] pCube1.e[138:139] ;
polyBevel3 -fraction 0.5 -offsetAsFraction 1 -autoFit 1 -segments 2 -worldSpace 1 -smoothingAngle 30 -fillNgons 1 -mergeVertices 1 -mergeVertexTolerance 0.0001 -miteringAngle 180 -angleTolerance 180 -ch 1 pCube1.e[54] pCube1.e[56] pCube1.e[58:59] pCube1.e[62] pCube1.e[64] pCube1.e[66:67] pCube1.e[69:72] pCube1.e[74] pCube1.e[76] pCube1.e[78] pCube1.e[80] pCube1.e[82] pCube1.e[84] pCube1.e[86] pCube1.e[88] pCube1.e[90] pCube1.e[92] pCube1.e[94] pCube1.e[96:100] pCube1.e[102:103] pCube1.e[105:108] pCube1.e[110] pCube1.e[112] pCube1.e[114] pCube1.e[116] pCube1.e[118] pCube1.e[120] pCube1.e[122] pCube1.e[124] pCube1.e[126] pCube1.e[128] pCube1.e[130] pCube1.e[132:136] pCube1.e[138:139];
// Result: polyBevel1 //
setAttr "polyBevel1.segments" 1;
setAttr "polyBevel1.fraction" 0.2;
select -r pCube1 ;
//
//
//
select -r pCube1.f[30] ;
select -tgl pCube1.f[126] ;
select -r pCube1.f[22:24] pCube1.f[26:30] pCube1.f[124:126] pCube1.f[129] ;
select -tgl pCube1.f[32] ;
select -tgl pCube1.f[127] ;
select -r pCube1.f[13:14] pCube1.f[22:30] pCube1.f[32:33] pCube1.f[35] pCube1.f[50:61] pCube1.f[122] pCube1.f[124:127] pCube1.f[129] ;
select -tgl pCube1.f[19] ;
select -tgl pCube1.f[36] ;
select -r pCube1.f[13:14] pCube1.f[19] pCube1.f[21:61] pCube1.f[122:129] ;
select -r pCube1.f[13:14] pCube1.f[19] pCube1.f[21:61] pCube1.f[122:129] ;
select -tgl pCube1.f[17] ;
select -tgl pCube1.f[18] ;
select -r pCube1.f[10:61] pCube1.f[122:129] ;
select -r pCube1.f[10:61] pCube1.f[122:129] ;
polyExtrudeFacet -constructionHistory 1 -keepFacesTogether 1 -pvx 0 -pvy 18.94050318 -pvz 0 -divisions 1 -twist 0 -taper 1 -off 0 -thickness 0 -smoothingAngle 30 pCube1.f[10:61] pCube1.f[122:129];
// Result: polyExtrudeFace6 //
setAttr "polyExtrudeFace6.localTranslate" -type double3 0 0 0.561432 ;
//
//
//
CreatePolygonCube;
polyCube -w 1 -h 1 -d 1 -sx 1 -sy 1 -sz 1 -ax 0 1 0 -cuv 4 -ch 1;
// Result: pCube4 polyCube4 //
move -r 0 0 19.085489 ;
scale -r 4.220598 1 1 ;
scale -r 1 1 2.27589 ;
move -r 0 23.766661 0.353976 ;
move -r 0 1.256653 -0.875374 ;
move -r 0 0.627245 -0.0170114 ;
// Warning: line 0: Cannot duplicate dagObjects and non-dagObjects in one command; Duplicating selected dagObject(s) only. //
duplicate -rr;
// Result: pCube5 //
move -r 0 -1.388916 0 ;
select -tgl pCube4 ;
scale -r 1 0.51969 1 ;
select -r pCube5 ;
move -r 0 0.213222 0 ;
//
//
//
select -r pCube5 ;
scale -r 1 0.567198 1 ;
duplicate -rr;
// Result: pCube7 //
move -r 0 0 3.068127 ;
rotate -r -os -fo 0 0 90 ;
scale -r 1 1 1.959888 ;
move -r 0 0 1.248968 ;
move -r 0 -0.260536 0 ;
select -cl  ;
CreatePolygonTorus;
polyTorus -r 1 -sr 0.5 -tw 0 -sx 20 -sy 20 -ax 0 1 0 -cuv 1 -ch 1;
// Result: pTorus1 polyTorus1 //
move -r 0 0 21.282374 ;
rotate -r -os -fo 0 0 -90 ;
move -r 0 25.635984 -0.367648 ;
select -cl  ;
select -r pCube7 ;
scale -r 1 3.532689 1 ;
select -r pTorus1 ;
setAttr "polyTorus1.radius" 1.5;
setAttr "polyTorus1.sectionRadius" 0.2;
move -r 0 0 -0.254292 ;
select -tgl pCube7 ;
move -r 0 -0.537235 -0.478274 ;
//
//
//
select -r pTorus2 ;
move -r 0 0 -1.115252 ;
select -r pCube7 ;
move -r 0 0.529639 0 ;
select -r pTorus2 ;
setAttr "polyTorus2.radius" 1.5;
setAttr "polyTorus2.sectionRadius" 0.2;
select -tgl pCube7 ;
move -r 0 -0.686094 0 ;
select -cl  ;
select -r pCube7 ;
move -r 0 0 -0.235067 ;
move -r 0 0.142105 0 ;
//
//
//
rename |pCube7 "LOCK_BODY" ;
// Result: LOCK_BODY //
hilite -r pTorus2 ;
select -r pTorus2 ;
rename |pTorus2 "LOCK_1" ;
// Result: LOCK_1 //
select -r pCube5 ;
rename |pCube5 "LOCK_A" ;
// Result: LOCK_A //
select -r pCube6 ;
rename |pCube6 "LOCK_B" ;
// Result: LOCK_B //
select -r pCube1 ;
rename |pCube1 "CHEST" ;
// Result: CHEST //
select -r LOCK_BODY  ;
parent LOCK_BODY  LOCK_1;
// Result: LOCK_1 //
select -r LOCK_1 ;
rotate -r -os -fo 0 15 0 ;
//
//
//
select -cl  ;
parent LOCK_1 CHEST ;
// Result: LOCK_1 //
select -r LOCK_B ;
parent LOCK_B CHEST ;
// Result: LOCK_B //
select -r LOCK_A ;
parent LOCK_A CHEST ;
// Result: LOCK_A //
select -r CHEST ;
select -r pCube2 ;
select -r pCube2 pCube3 pCube4 pTorus1 ;
doDelete;


    '''

    mel.eval(recorded_macro)
    set_scale_keys(target='CHEST', keyframes=[[0.001, 57], [0.1, 63]])
    set_position_keys(target='CHEST', keyframes=[[[-3.892, 0.764, 0.349], 57, [1, 1]],
                                               [[-3.892, 2.297, 0.349], 61, [1, 1]],
                                               [[-3.892, 0.764, 0.349], 63, [1, 1]]])
    cmds.rotate('CHEST')
    cmds.move(-3.941, -1.533, 0.061, absolute=True)
    cmds.parent('CHEST', 'land')


def create_and_animate_trees():
    """
    Function uses the create_palm() support function to create and animate some palm trees.
    It was created to show how to create basic geometry objects, use instances and use modificators.
    """

    palm = create_palm(diameter=1.3, segs_num=20, leafs_num=9, bending=34, id_num=1, anim_start=11, anim_end=26)
    cmds.currentTime(55)
    cmds.refresh(f=True)
    cmds.delete(palm, ch=True)

    cmds.rotate(-0.051025, 1.69211, 0.366333, palm, absolute=True)  # Rotate the palm
    cmds.move(-8.5, -4.538, 18.1, palm, absolute=True)  # Position the palm
    cmds.parent(palm, 'land', relative=True)

    palm = create_palm(diameter=1.6, segs_num=20, leafs_num=9, bending=40, id_num=2, anim_start=40, anim_end=45)
    cmds.refresh(f=True)
    cmds.delete(palm, ch=True)
    cmds.rotate(0.0226778, 0.247746, 1.71606, palm)
    cmds.move(28, -6.3, -2.5, palm)
    cmds.parent(palm, 'land', relative=True)


    palm = create_palm(diameter=1.1, segs_num=18, leafs_num=9, bending=24, id_num=3, anim_start=20, anim_end=35)
    cmds.refresh(f=True)
    cmds.delete(palm, ch=True)
    cmds.rotate(0.0226778, 0.247746, -1.94985, palm)
    cmds.move(34, -2.5, -34, palm)
    cmds.parent(palm, 'land', relative=True)


    palm = create_palm(diameter=1.1, segs_num=24, leafs_num=9, bending=24, id_num=4, anim_start=25, anim_end=40)
    cmds.refresh(f=True)
    cmds.delete(palm, ch=True)
    cmds.rotate(0.0226778, 0.244222, -1.03672, palm)
    cmds.move(14, -2.5, -19, palm)
    cmds.parent(palm, 'land', relative=True)





def change_hierarchy_and_animate():
    """
    Function modifies the hierarchy of scen and creates some final animations, that ware not possible to create earlier.
    It also creates cameras and lights.
    """
    cmds.lookThru( 'perspView', 'RenderCamera1')

    top_locator = cmds.spaceLocator()
    objects_list = ['land', 'water', 'cloud', 'shark', ]

    for obj in objects_list:
        cmds.parent(obj, top_locator)

    cmds.setKeyframe(top_locator, attribute='rotateY', v=20, time=260, itt="plateau", ott="plateau")
    cmds.setKeyframe(top_locator, attribute='rotateY', v=0, time=0, itt="linear", ott="linear")

    dome_light = cmds.polySphere(r=500);
    cmds.polyNormal(dome_light, normalMode=0)

    cmds.setAttr(dome_light[0]+".miDeriveFromMaya", 0)
    cmds.setAttr(dome_light[0]+".miVisible", 0)
    cmds.setAttr(dome_light[0]+".miShadow", 0)
    cmds.rename(dome_light[0], "dome_light")

    area_light = cmds.shadingNode('areaLight', asLight=True)
    cmds.move(0, 0, 0, area_light, absolute=True)
    cmds.rotate(0, 0, 0, area_light, absolute=True)
    cmds.scale(25, 25, 25, area_light, absolute=True)

    cmds.setAttr(area_light+".intensity", 8)
    cmds.setAttr(area_light+".areaLight", 1)
    cmds.setAttr(area_light+".areaType", 1)
    cmds.setAttr(area_light+".decayRate", 2)


def create_and_assign_materials():
    """
    Function creates and applies materials to the objects
    It was created to show how to use the Material Manager.
    """

    light_dome_mat = cmds.shadingNode("surfaceShader", asShader=True)
    cmds.setAttr(light_dome_mat+".outColorR", 1.0)
    cmds.setAttr(light_dome_mat+".outColorG", 1.0)
    cmds.setAttr(light_dome_mat+".outColorB", 1.0)
    light_dome_sg= cmds.sets(renderable=True,noSurfaceShader=True,empty=True)
    cmds.connectAttr('%s.outColor' %light_dome_mat ,'%s.surfaceShader' %light_dome_sg)

    land_mat = cmds.shadingNode("lambert", asShader=True)
    cmds.setAttr(land_mat+".outColorR", 1.0)
    cmds.setAttr(land_mat+".outColorG", 0.75)
    cmds.setAttr(land_mat+".outColorB", 0.45)
    land_sg= cmds.sets(renderable=True,noSurfaceShader=True,empty=True)
    cmds.connectAttr('%s.outColor' %land_mat ,'%s.surfaceShader' %land_sg)
    cmds.sets("land", e=True, forceElement=land_sg)

    wood_mat = cmds.shadingNode("lambert", asShader=True)
    cmds.setAttr(wood_mat+".outColorR", 0.18)
    cmds.setAttr(wood_mat+".outColorG", 0.13)
    cmds.setAttr(wood_mat+".outColorB", 0.13)
    wood_sg= cmds.sets(renderable=True,noSurfaceShader=True,empty=True)
    cmds.connectAttr('%s.outColor' %wood_mat ,'%s.surfaceShader' %wood_sg)
    #cmds.sets("land", e=True, forceElement=wood_sg)

    leaf_mat = cmds.shadingNode("lambert", asShader=True)
    cmds.setAttr(leaf_mat+".outColorR", 0.4)
    cmds.setAttr(leaf_mat+".outColorG", 1.0)
    cmds.setAttr(leaf_mat+".outColorB", 0.3)
    leaf_sg= cmds.sets(renderable=True,noSurfaceShader=True,empty=True)
    cmds.connectAttr('%s.outColor' %leaf_mat ,'%s.surfaceShader' %leaf_sg)

    gray_mat = cmds.shadingNode("lambert", asShader=True)
    cmds.setAttr(gray_mat+".outColorR", 0.5)
    cmds.setAttr(gray_mat+".outColorG", 0.5)
    cmds.setAttr(gray_mat+".outColorB", 0.5)
    gray_sg= cmds.sets(renderable=True,noSurfaceShader=True,empty=True)
    cmds.connectAttr('%s.outColor' %gray_mat ,'%s.surfaceShader' %gray_sg)

    water_mat = cmds.shadingNode("mia_material_x", asShader=True)
    cmds.setAttr(water_mat+".diffuseR", 0.0)
    cmds.setAttr(water_mat+".diffuseG", 0.209)
    cmds.setAttr(water_mat+".diffuseB", 0.202)
    cmds.setAttr(water_mat+".refl_gloss", 0.84)
    cmds.setAttr(water_mat+".reflectivity", 0.6)
    cmds.setAttr(water_mat+".diffuse_roughness", 0.16)
    cmds.setAttr(water_mat+".refr_ior", 1.3)
    cmds.setAttr(water_mat+".transparency", 0.43*0.435)
    cmds.setAttr(water_mat+".refr_gloss", 0.76)
    water_sg= cmds.sets(renderable=True,noSurfaceShader=True,empty=True)
    cmds.connectAttr('%s.message' %water_mat ,'%s.miPhotonShader' %water_sg)
    cmds.connectAttr('%s.message' %water_mat ,'%s.miShadowShader' %water_sg)
    cmds.connectAttr('%s.message' %water_mat ,'%s.miMaterialShader' %water_sg)

    for obj in cmds.ls(geometry=True, ):
        if "dome_light" in obj:
            cmds.sets(obj, e=True, forceElement=light_dome_sg)
        if "LOCK" in obj:
            cmds.sets(obj, e=True, forceElement=gray_sg)
        if any(x in obj for x in ['segment', 'CHEST']):
            cmds.sets(obj, e=True, forceElement=wood_sg)
        if "leaf" in obj:
            cmds.sets(obj, e=True, forceElement=leaf_sg)
        if "water" in obj:
            cmds.sets(obj, e=True, forceElement=water_sg)

    return 0
    # Simple, gray material for cloud and shark:
    mat_id = MaxPlus.Class_ID(1890604853, 1242969684)  # Class_ID of Arch & Design material
    m = MaxPlus.Factory.CreateMaterial(mat_id)
    m.Diffuse = MaxPlus.Color(0.84, 0.84, 0.84)  # Set parameters of the material
    m.ParameterBlock.refl_weight.Value = 0
    m.ParameterBlock.diff_rough.Value = 1
    m.SetName(MaxPlus.WStr('Gray_material'))

    # Assign material to the shark, cloud and metal parts of the chest. Find them by name.
    for name in ['cloud', 'shark', "lock", "lock001", "lock_ring", "chest_metal_part", "Lock_Body"]:
        node = MaxPlus.INode.GetINodeByName(name)
        node.Material = m
    pass

    # Water material, more material parameters included:
    m = MaxPlus.Factory.CreateMaterial(mat_id)
    m.ParameterBlock.diff_color.Value = MaxPlus.Color(0, 0.208633, 0.201736)
    m.ParameterBlock.diff_rough.Value = 0.0
    m.ParameterBlock.diff_weight.Value = 1.0
    m.ParameterBlock.refl_color.Value = MaxPlus.Color(1, 1, 1)
    m.ParameterBlock.refl_gloss.Value = 0.840000092983
    m.ParameterBlock.refl_samples.Value = 8
    m.ParameterBlock.refl_interp.Value = False
    m.ParameterBlock.refl_hlonly.Value = False
    m.ParameterBlock.refl_metal.Value = False
    m.ParameterBlock.refl_weight.Value = 0.600000023842
    m.ParameterBlock.refr_color.Value = MaxPlus.Color(0.435294, .435294, 0.435294)
    m.ParameterBlock.refr_gloss.Value = 0.760000050068
    m.ParameterBlock.refr_samples.Value = 8
    m.ParameterBlock.refr_interp.Value = False
    m.ParameterBlock.refr_ior.Value = 1.30000007153
    m.ParameterBlock.refr_weight.Value = 0.429999947548
    m.ParameterBlock.refr_trans_on.Value = False
    m.ParameterBlock.refr_transc.Value = MaxPlus.Color(1, 1, 1)
    m.ParameterBlock.refr_transw.Value = 0.0
    m.ParameterBlock.anisotropy.Value = 1.0
    m.ParameterBlock.anisoangle.Value = 0.0
    m.ParameterBlock.aniso_mode.Value = 0
    m.ParameterBlock.aniso_channel.Value = 0
    m.ParameterBlock.refl_func_fresnel.Value = True
    m.ParameterBlock.refl_func_low.Value = 0.20000000298
    m.ParameterBlock.refl_func_high.Value = 1.0
    m.ParameterBlock.refl_func_curve.Value = 5.0
    m.ParameterBlock.refl_falloff_on.Value = True
    m.ParameterBlock.refl_falloff_dist.Value = 19.4505996704
    m.ParameterBlock.refl_falloff_color_on.Value = True
    m.ParameterBlock.refl_falloff_color.Value = MaxPlus.Color(0.2, 0.2, 0.2)
    m.ParameterBlock.opts_refl_depth.Value = 4
    m.ParameterBlock.refl_cutoff.Value = 0.00999999977648
    m.ParameterBlock.refr_falloff_on.Value = True
    m.ParameterBlock.refr_falloff_dist.Value = 1.65000009537
    m.ParameterBlock.refr_falloff_color_on.Value = True
    m.ParameterBlock.refr_falloff_color.Value = MaxPlus.Color(0.12549, 0.988235, 1)
    m.ParameterBlock.opts_refr_depth.Value = 6
    m.ParameterBlock.refr_cutoff.Value = 0.00999999977648
    m.ParameterBlock.opts_indirect_multiplier.Value = 1.0
    m.ParameterBlock.opts_fg_quality.Value = 1.0
    m.ParameterBlock.inter_density.Value = 2
    m.ParameterBlock.intr_refl_samples.Value = 2
    m.ParameterBlock.intr_refl_ddist_on.Value = False
    m.ParameterBlock.intr_refl_ddist.Value = 0.0
    m.ParameterBlock.intr_refr_samples.Value = 2
    m.ParameterBlock.single_env_sample.Value = False
    m.ParameterBlock.opts_round_corners_on.Value = False
    m.ParameterBlock.opts_round_corners_radius.Value = 10.0
    m.ParameterBlock.opts_round_corners_any_mtl.Value = True
    m.ParameterBlock.opts_ao_on.Value = False
    m.ParameterBlock.opts_ao_exact.Value = False
    m.ParameterBlock.opts_ao_use_global_ambient.Value = False
    m.ParameterBlock.opts_ao_samples.Value = 16
    m.ParameterBlock.opts_ao_distance.Value = 4.0
    m.ParameterBlock.opts_ao_dark.Value = MaxPlus.Color(0.2, 0.2, 0.2)
    m.ParameterBlock.opts_ao_ambient.Value = MaxPlus.Color(0, 0, 0)
    m.ParameterBlock.opts_ao_do_details.Value = True
    m.ParameterBlock.opts_no_area_hl.Value = True
    m.ParameterBlock.opts_1sided.Value = False
    m.ParameterBlock.opts_do_refractive_caustics.Value = False
    m.ParameterBlock.opts_skip_inside.Value = True
    m.ParameterBlock.opts_hl_to_refl_balance.Value = 1.0
    m.ParameterBlock.opts_backface_cull.Value = False
    m.ParameterBlock.opts_propagate_alpha.Value = False
    m.ParameterBlock.diff_color_map_on.Value = True
    m.ParameterBlock.diff_rough_map_on.Value = True
    m.ParameterBlock.refl_color_map_on.Value = True
    m.ParameterBlock.refl_gloss_map_on.Value = True
    m.ParameterBlock.refr_color_map_on.Value = False
    m.ParameterBlock.refr_gloss_map_on.Value = True
    m.ParameterBlock.refr_ior_map_on.Value = True
    m.ParameterBlock.refr_transc_map_on.Value = True
    m.ParameterBlock.refr_transw_map_on.Value = True
    m.ParameterBlock.anisotropy_map_on.Value = True
    m.ParameterBlock.anisoangle_map_on.Value = True
    m.ParameterBlock.refl_falloff_color_map_on.Value = True
    m.ParameterBlock.refr_falloff_color_map_on.Value = True
    m.ParameterBlock.indirect_multiplier_map_on.Value = True
    m.ParameterBlock.fg_quality_map_on.Value = True
    m.ParameterBlock.ao_dark_map_on.Value = True
    m.ParameterBlock.ao_ambient_map_on.Value = True
    m.ParameterBlock.bump_map_on.Value = False
    m.ParameterBlock.displacement_map_on.Value = True
    m.ParameterBlock.cutout_map_on.Value = True
    m.ParameterBlock.environment_map_on.Value = False
    m.ParameterBlock.add_color_map_on.Value = True
    m.ParameterBlock.radius_map_on.Value = True
    m.SetName(MaxPlus.WStr('Water_material'))

    node = MaxPlus.INode.GetINodeByName('water')
    node.Material = m


    # Sand:
    m = MaxPlus.Factory.CreateMaterial(mat_id)
    m.Diffuse = MaxPlus.Color(1, 0.74, 0.45)
    m.ParameterBlock.refl_weight.Value = 0
    m.ParameterBlock.diff_rough.Value = 0
    m.SetName(MaxPlus.WStr('Sand_material'))

    node = MaxPlus.INode.GetINodeByName('land')
    node.Material = m

    # Wood:
    m = MaxPlus.Factory.CreateMaterial(mat_id)
    m.Diffuse = MaxPlus.Color(0.18, 0.13, 0.13)
    m.ParameterBlock.refl_weight.Value = 0
    m.ParameterBlock.diff_rough.Value = 0
    m.SetName(MaxPlus.WStr('Wood_material'))

    node = MaxPlus.INode.GetINodeByName('chest')
    node.Material = m
    # Assign material 'Wood_material' to nodes with prefix 'Palm' in name
    append_material_by_prefix(prefix='Palm', material=m)


    # Leafs:
    m = MaxPlus.Factory.CreateMaterial(mat_id)
    m.Diffuse = MaxPlus.Color(0.4, 1, 0.3)
    m.ParameterBlock.refl_weight.Value = 0
    m.ParameterBlock.diff_rough.Value = 0
    m.SetName(MaxPlus.WStr('Leaf_material'))

    append_material_by_prefix(prefix='leaf', material=m)


#
#
# Gui and interface:
#
#


class DataTable:
    """
    Object stores the parameters of currently running instance of script. It also runs the functions
    and makes callbacks to UI elements easier.
    """

    target_list = None
    target_label = None
    scores_list = []
    next_step = 0  # the step that should be performed next (when running the script step-by-step)
    ignore_steps = False  # if ignore_steps is false the animation is step by step

    def __init__(self):
        pass

    def run(self, text, function, path=None):
        """
        Run the script: create the scene. It can run step-by-step and stop after every part or run every function
        one after another. The function also measures an execution time of commands and updates the UI elements.

        :param text: string - Name of the current step that will be displayed in the UI and scores table.
        :param function: function() - Function that will be run.
        :param path: string - Additional parameter: path that can be passed to the function as parameter:
                              required by some functions.
        """

        self.target_label.setText(text)  # Update the label of UI
        if path is None:  # If no path was passed as argument, then do not pass this variable to target function
            ts = time.time()  # Start measuring time
            function()  # Execute the function passed as an argument
        else:
            ts = time.time()
            function(path)  # if path was passed then pass it to the target function
        te = time.time()  # Record the ending time of command
        score = [text, te - ts]  # Measure the interval
        self.scores_list.append(score)  # append the

        try:
            self.target_list.addItem(QtGui.QListWidgetItem(str(score)))  # Add measured time to scores list in UI
        except:
            pass

    def save(self):
        """
        Funcrtion saves the execution times of commands to the file.
        """

        i = 0
        scores = []

        while i < self.target_list.count():
            scores.append(self.target_list.item(i).text())
            i += 1

        path = QtGui.QFileDialog.getExistingDirectory(None, 'Wybierz folder do zapisu pliku wyniki.txt',
                                                      'D:/Dane/Projekty/licencjat/')
        with open(path + '/wyniki_Mays.txt', 'w') as file_:
            for score in scores:
                file_.write(score + '\n')

    def reset(self):
        """
        Function resets the max file and parameters of this object to the initial state.
        """

        self.max_step = 0
        cmds.file(newFile=1, force=1)  # Force creation of a new scene
        pass


class GUI(QtGui.QDialog):
    path = "C:/"

    def __init__(self):

        # set maya main window as parent or it will disappear quickly:
        main_window_ptr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(long(main_window_ptr), QtGui.QWidget)

        super(GUI, self).__init__(mayaMainWindow)  # Initialize with mayaMainWindow as a parent

        self.resize(250, 150)  # Set the size of window
        self.center()
        self.setWindowTitle('Skrypt - 3Ds Max')  # Set the title of window
        self.setWindowFlags(QtCore.Qt.Tool)  # The tool window will always be kept on top of parent (maya_main_window)

        # Delete UI on close to avoid winEvent error
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        grid = QtGui.QGridLayout()  # Create a grid layout
        grid_internal = QtGui.QGridLayout()
        self.label_info = QtGui.QLabel('Uruchom skrypt wciskajac `start`')  # Create a label GUI element
        btn_step = QtGui.QPushButton('Krok po kroku')  # Create a button
        btn_start = QtGui.QPushButton('Wszystkie kroki')
        self.connect(btn_start, SIGNAL("clicked()"), self.fn_no_steps)  # Connect button to function
        self.connect(btn_step, SIGNAL("clicked()"), self.fn_step)
        self.times_list = QtGui.QListWidget(self)  # Create a list widget
        btn_save = QtGui.QPushButton('Zapisz wyniki')
        btn_reset = QtGui.QPushButton('Wyczysc scene')

        grid.addWidget(self.label_info, 0, 0)  # Add the widget to the layout

        grid_internal.addWidget(btn_step, 0, 0)
        grid_internal.addWidget(btn_start, 0, 1)

        grid.addLayout(grid_internal, 1, 0)
        grid.addWidget(self.times_list, 2, 0)
        grid.addWidget(btn_save, 3, 0)
        grid.addWidget(btn_reset, 4, 0)

        self.data_table = DataTable()
        self.data_table.target_list = self.times_list
        self.data_table.target_label = self.label_info

        self.connect(btn_reset, SIGNAL("clicked()"), self.data_table.reset)
        self.connect(btn_save, SIGNAL("clicked()"), self.data_table.save)

        self.setLayout(grid)  # Set the layout of the window

    def center(self):
        """
        Function places window on the center of the screen. It is not neccesary for script to run.
        """

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def fn_step(self):
        """
        Run function step-by-step: make one step.
        """

        self.data_table.ignore_steps = False
        self.fn_start()

    def fn_no_steps(self):
        """
        Run function: make all the steps.
        """

        self.data_table.ignore_steps = True
        self.fn_start()

    def fn_start(self):
        """
        Function runs other functions in a right order and with right parameters.
        """
        while not os.path.isfile(self.path + '/land.obj'):  # checks if the folder includes necessary file.
            # If not, then shows the QFileDialog that makes it possible to select the right one.

            self.path = QtGui.QFileDialog.getExistingDirectory(self, 'Wybierz folder z dodatkowymi plikami',
                                                               'D:/Dane/Projekty/licencjat/')
            print self.path

        functions_with_names = [["Ustawianie sceny", prepare_scene, self.path],
                                ["Importowanie podstawowych obiektow", import_and_animate_basic_meshes, self.path],
                                ["Tworzenie pletwy rekina i chmury", create_shark_and_cloud, None],
                                ["Tworzenie skrzynki za pomoca Macro", create_chest, None],
                                ["Tworzenie i animowanie drzew", create_and_animate_trees, None],
                                ["Zmiana hierarhii obiektow, koncowa animacja", change_hierarchy_and_animate, None],
                                ["Tworzenie i przypisywanie materialow", create_and_assign_materials, None]]

        if self.data_table.ignore_steps:
            for action_num in xrange(self.data_table.next_step, len(functions_with_names)):
                line = functions_with_names[action_num]
                self.data_table.run(text=line[0], function=line[1], path=line[2])
        else:
            action_num = self.data_table.next_step
            self.data_table.next_step += 1
            line = functions_with_names[action_num]
            self.data_table.run(text=line[0], function=line[1], path=line[2])


if __name__ == "__main__":

    # Development workaround for winEvent error when running
    # the script multiple times
    try:
        ui.close()
    except:
        pass

    ui = GUI()
    ui.show()

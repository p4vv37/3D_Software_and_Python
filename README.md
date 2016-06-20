# Python API in 3D computer graphics software: examplary scripts
Example of Python scripts for Autodesk 3D Studio Max, Autodesk Maya and Blender. 
Those scripts use Python API to create simmilar scene in: Autodesk 3D Studio Max, Autodesk Maya and Blender.
Created to show the basics of using Python in those applications.

Every script has a number of suport functions and seven major functions:
- prepare_scene(path) - The function sets the basic parameters of the scene: time range, tangent type of keyframes and render settings.
- import_and_animate_basic_meshes(path) - This function imports some objects and animates them. It was created to show how to import objects and present one way of creating keyframes of animation.
- create_shark_and_cloud() - Creates meshes from vertex and face data. Similar functions can be used in importer plugin.
- create_chest() - Function creates an object with a use ofrecorded macros, if such function is avaible in software. Macros are a very simple way of creating basic scripts.
- create_and_animate_trees() -  Function uses the create_palm() support function to create and animate some palm trees. It was created to show how to create basic geometry objects, use instances and use modificators.
- change_hierarchy_and_animate() -  Function modifies the hierarchy of scen and creates some final animations, that ware not possible to create earlier. It also creates cameras and lights.
- create_and_assign_materials() - Function creates and applies materials to the objects. It was created to show how to handle materials.

All scripts have simple GUIs

## How to use:

- Download the content of the "common" directory. Script will ask for path to those files before running
- Read the Readme.md file inside directory wit a script for choosen software and fallow the instructions. Every software has a different way of running scripts

## License:

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 
 To the extent possible under law, [Paweł Kowalski](http://pkowalski.com) has waived all copyright and related or neighboring rights to this work.

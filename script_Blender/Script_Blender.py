bl_info = {
    "name": "MyScript",
    "author": "Pawe? Kowalski",
    "version": (1, 0),
    "blender": (2, 76, "b"),
    "location": "Krakow",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "category": ""}

import bpy
import os
import random
import math
from bpy_extras.io_utils import ExportHelper


#
#
# Blender stuff, mostly Gui:
#
#

# Properties:

class ActionsRecordsItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Action name", default="None")
    time = bpy.props.StringProperty(name="Execution  time", default="0.0")


class MyColl(bpy.types.PropertyGroup):
    label = bpy.props.StringProperty()
    description = bpy.props.StringProperty()


# Operators:

class RunActions(bpy.types.Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "object.run_actions"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Run actions"

    # ExportHelper mixin class uses this
    filename_ext = ".obj"

    filter_glob = bpy.props.StringProperty(
            default="*.obj",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    directory = bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        if os.path.isfile(os.path.join(self.directory, "water.obj")):
            print("ok")
            return {'FINISHED'}
        else:
            return bpy.ops.my_blender_script.run_actions('INVOKE_DEFAULT')

    def invoke(self, context, event):
        if not self.filepath:
            context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ResetOperator(bpy.types.Operator):
    bl_idname = "object.reset_operator"
    bl_label = "Reset the scene"

    def execute(self, context):
        for obj in bpy.data.objects:
            obj.select = True
        bpy.ops.object.delete()
        bpy.context.scene.actions_records.clear()
        bpy.app.handlers.scene_update_pre.append(collhack)
        return {'FINISHED'}


class SaveToFileOperator(bpy.types.Operator):
    bl_idname = "object.save_to_file_operator"
    bl_label = "Simple Object Operator"
    save_path = bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        path = self.save_path
        with open(path + '/wyniki_Blender.txt', 'w') as file_:
            for score in bpy.context.scene.actions_records:
                file_.write(score.name + ": " + score.time + '\n')
        return {'FINISHED'}


class ExecuteAll(bpy.types.Operator):
    bl_idname = "object.execute_all"
    bl_label = "File browser Operator"
    filepath = bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        bpy.context.scene.step_by_step = False
        run()
        # while not os.path.isfile(
        #                 context.scene.content_path + '/land.obj'):  # checks if the folder includes necessary file.
        #     # If not, then shows the QFileDialog that makes it possible to select the right one.
        #
        #     context.scene.content_path = self.filepath
        #     print("Path:")
        #     print(context.scene.content_path)
        #
        #         self.label_info.setText("Rozpoczeto dzialanie skryptu")
        #
        # functions_with_names = [["Ustawianie sceny", prepare_scene, self.path],
        #                         ["Importowanie podstawowych obiektow", import_and_animate_basic_meshes, self.path],
        #                         ["Tworzenie pletwy rekina i chmury", create_shark_and_cloud, None],
        #                         ["Tworzenie skrzynki za pomoca Macro", create_chest, None],
        #                         ["Tworzenie i animowanie drzew", create_and_animate_trees, None],
        #                         ["Zmiana hierarhii obiektow, koncowa animacja", change_hierarchy_and_animate, None],
        #                         ["Tworzenie i przypisywanie materialow", create_and_assign_materials, None]]
        #
        # if self.data_table.ignore_steps:
        #     for action_num in xrange(self.data_table.next_step, len(functions_with_names)):
        #         line = functions_with_names[action_num]
        #         self.data_table.run(text=line[0], function=line[1], path=line[2])
        # else:
        #     action_num = self.data_table.next_step
        #     self.data_table.next_step += 1
        #     line = functions_with_names[action_num]
        #     self.data_table.run(text=line[0], function=line[1], path=line[2])
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ExecuteStepByStep(bpy.types.Operator):
    bl_idname = "object.step_by_step"
    bl_label = "File browser Operator"
    filepath = bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        bpy.context.scene.step_by_step = True
        run()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Other GUI classes:


class ActionsList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(0.3)
            split.label(item.label)
            split.label(item.description)

        elif self.layout_type in {'GRID'}:
            pass


class MyScriptPanel(bpy.types.Panel):
    bl_label = "Skrypt - Blender"
    bl_idname = "OBJECT_PT_myscript"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        col = context.scene.col
        idx = context.scene.col_idx
        message = context.scene.gui_message

        if idx >= len(col):
            text = "(index error)"
        else:
            text = col[idx].name

        layout.label(message)
        col = layout.column(align=True)
        row_1 = col.row(align=True)
        row_1.operator("object.run_actions", text="Krok po kroku")
        row_1.operator("object.run_actions", text="Wszystkie kroki")
        row_2 = col.row(align=True)
        row_2.template_list("ActionsList", "", context.scene, "col", context.scene, "col_idx")
        col_23 = row_2.column(align=True)
        col_23.operator("object.save_to_file_operator", text="Zapisz wyniki")
        # col_23 = col.row(align=True)
        col_23.operator("object.reset_operator", text="Wyczysc scene")


# Functions

def run(text, function):
    print_to_ui(text)  # Update the label of UI
    ts = time.time()  # Start measuring time
    function()  # Execute the function passed as an argument
    te = time.time()  # Record the ending time of command
    interval = te - ts  # Measure the interval
    add_new_item_to_list(text, interval)  # append the

    try:
        self.target_list.addItem(QtGui.QListWidgetItem(str(score)))  # Add measured time to scores list in UI
    except:
        pass

def collhack(scene):
    bpy.app.handlers.scene_update_pre.remove(collhack)

    try:
        scene.col.clear()
    except:
        pass
    i = 1
    for new_item in bpy.context.scene.actions_records:
        item = scene.col.add()
        item.label = new_item.name
        item.description = str(new_item.time)
        item.name = " ".join((str(i), item.label, item.description))
        i += 1


def add_new_item_to_list(name, time):
    new_item = bpy.context.scene.actions_records.add()
    new_item.name = str(name)
    new_item.time = str(time)
    bpy.app.handlers.scene_update_pre.append(collhack)


def print_to_ui(text):
    bpy.context.scene.gui_message = text


def register():
    bpy.types.Scene.gui_message = bpy.props.StringProperty(name="Current message",
                                                           default="Uruchom skrypt wciskajac `start`")
    bpy.types.Scene.content_path = bpy.props.StringProperty(name="Path to content", default='C:/')
    bpy.types.Scene.next_step = bpy.props.IntProperty(name="Next step of step-by-step execution", default=0)
    bpy.types.Scene.step_by_step = bpy.props.BoolProperty(name="Next step of step-by-step execution", default=True)
    bpy.utils.register_class(ActionsRecordsItem)
    bpy.types.Scene.actions_records = bpy.props.CollectionProperty(type=ActionsRecordsItem)
    bpy.utils.register_class(RunActions)

    bpy.utils.register_module(__name__)
    bpy.types.Scene.col = bpy.props.CollectionProperty(type=MyColl)
    bpy.types.Scene.col_idx = bpy.props.IntProperty(default=0)

    bpy.context.scene.actions_records
    bpy.app.handlers.scene_update_pre.append(collhack)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.col
    del bpy.types.Scene.col_idx
    del bpy.types.Scene.content_path
    del bpy.types.Scene.actions_records


#
#
# Start.
#
#


if __name__ == "__main__":
    register()
    for obj in bpy.data.objects:
        obj.select = True
    bpy.ops.object.delete()
    bpy.context.scene.actions_records.clear()
    my_item = bpy.context.scene.actions_records.add()
    my_item.name = "Zadanie"
    my_item.time = "czas"
    bpy.app.handlers.scene_update_pre.append(collhack)

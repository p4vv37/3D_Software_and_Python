import bpy
import os

from bpy_extras.io_utils import ExportHelper

class RunActions(bpy.types.Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "my_blender_script.run_actions"  # important since its how bpy.ops.import_test.some_data is constructed
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


# Only needed if you want to add into a dynamic menu
def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(RunActions.bl_idname, text="My Blender Script Operator")

# Register and add to the file selector
bpy.utils.register_class(RunActions)
bpy.types.INFO_MT_file_export.append(menu_func)


# test call
bpy.ops.my_blender_script.run_actions('INVOKE_DEFAULT')
bpy.ops.my_blender_script.run_actions('INVOKE_DEFAULT')
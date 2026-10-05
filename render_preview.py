import bpy
import math
import os

root = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(root, 'PlushieCollection.blend'))

bpy.ops.object.camera_add(location=(0, -31, 6.2), rotation=(math.radians(79), 0, 0))
cam = bpy.context.object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 29
bpy.context.scene.camera = cam

for loc, energy, size in [((-10,-12,11),1800,7),((10,-8,9),1300,6),((0,5,12),1000,5)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light=bpy.context.object
    light.data.energy=energy
    light.data.shape='DISK'
    light.data.size=size
    direction=(bpy.context.scene.cursor.location-light.location).to_track_quat('-Z','Y')
    light.rotation_euler=direction.to_euler()

bpy.context.scene.render.engine='BLENDER_EEVEE'
bpy.context.scene.render.resolution_x=1800
bpy.context.scene.render.resolution_y=600
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.render.image_settings.file_format='PNG'
bpy.context.scene.render.filepath=os.path.join(root,'PlushieCollection_preview.png')
bpy.context.scene.world.color=(0.025,0.025,0.035)
bpy.context.scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.render.render(write_still=True)

import bpy,math,os
from mathutils import Vector
root=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'PickupCollection.blend'))
order=['SM_CommonCapsule','SM_UncommonCapsule','SM_RareCapsule','SM_EpicCapsule','SM_GoldenCapsule','SM_Bomb','SM_MegaBomb','SM_Magnet','SM_TicketCapsule','SM_JackpotSphere','SM_GoldenPlush','SM_RainbowSphere','SM_StickyCapsule','SM_HeavySphere','SM_BouncyBall','SM_CrystalCapsule','SM_DupeCapsule','SM_MysteryPlush','SM_MysteryCapsule','SM_Coin']
assets=[bpy.data.objects[n] for n in order]
for i,o in enumerate(assets):
    row=i//10; col=i%10
    o.location=((col-4.5)*2.65, 0, (1-row)*3.15)
bpy.ops.object.camera_add(location=(0,-26,3.1),rotation=(math.pi/2,0,0))
cam=bpy.context.object; cam.data.type='ORTHO'; cam.data.ortho_scale=28.5; bpy.context.scene.camera=cam
for loc,energy,size in [((-10,-10,13),2200,8),((10,-7,10),1600,7),((0,8,14),1800,7)]:
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=energy; l.data.shape='DISK'; l.data.size=size
    l.rotation_euler=(Vector((0,1.5,1.0))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.render.engine='BLENDER_EEVEE'; bpy.context.scene.render.resolution_x=1800; bpy.context.scene.render.resolution_y=800; bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.render.image_settings.file_format='PNG'; bpy.context.scene.render.filepath=os.path.join(root,'PickupCollection_preview.png')
bpy.context.scene.world.color=(.018,.02,.028); bpy.context.scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.render.render(write_still=True)

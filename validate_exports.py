import bpy, os
root=os.path.dirname(os.path.abspath(__file__))
folder=os.path.join(root,'exports')
expected=None
for filename in sorted(f for f in os.listdir(folder) if f.lower().endswith('.fbx')):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=os.path.join(folder,filename),automatic_bone_orientation=False)
    arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    assert len(arms)==1, (filename,len(arms))
    arm=arms[0]
    bones=tuple(sorted(b.name for b in arm.data.bones))
    if expected is None: expected=bones
    assert bones==expected,(filename,bones,expected)
    assert arm.location.length < 0.0001,(filename,tuple(arm.location))
    rootbone=arm.data.bones.get('root')
    assert rootbone and abs(rootbone.head_local.x)<0.0001,(filename,tuple(rootbone.head_local))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(meshes)==1,(filename,'expected one joined skeletal mesh',len(meshes))
    image_nodes=[]
    for mesh in meshes:
        for material in mesh.data.materials:
            if material and material.use_nodes:
                image_nodes += [n for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    assert image_nodes,(filename,'No imported image texture node')
    polygons=len(meshes[0].data.polygons)
    assert polygons<5000,(filename,'plush polygon budget exceeded',polygons)
    print('VALID',filename,'origin',tuple(round(v,4) for v in arm.location),'bones',len(bones),'textures',len(image_nodes),'polygons',polygons)
print('ALL_EXPORTS_VALID')

import bpy,os
root=os.path.dirname(os.path.abspath(__file__))
folder=os.path.join(root,'pickup_exports')
files=sorted(f for f in os.listdir(folder) if f.lower().endswith('.fbx'))
assert len(files)==20,len(files)
for f in files:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=os.path.join(folder,f))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(meshes)==1,(f,len(meshes))
    o=meshes[0]
    assert o.location.length<.0001,(f,tuple(o.location))
    assert abs(o.data.vertices[0].co.x)<100 # sanity check for corrupt geometry
    assert len(o.data.materials)>0,(f,'no materials')
    if f in {'SM_Bomb.fbx','SM_MegaBomb.fbx','SM_BouncyBall.fbx','SM_HeavySphere.fbx'}:
        images=[]
        for m in o.data.materials:
            if m and m.use_nodes:images += [n for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
        assert images,(f,'baked icon texture missing after FBX round trip')
    assert len(o.data.polygons)<2500,(f,'polygon budget exceeded',len(o.data.polygons))
    print('VALID',f,'origin',tuple(round(v,4) for v in o.location),'materials',len(o.data.materials),'polygons',len(o.data.polygons))
print('ALL_20_STATIC_MESHES_VALID')

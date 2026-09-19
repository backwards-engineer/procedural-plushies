import bpy, os
from mathutils import Vector
root=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'PlushieCollection.blend'))
o=bpy.data.objects['Burplepup_SK']
uv=o.data.uv_layers.active.data
targets=[(-.32,-.76,1.62),(.32,-.76,1.62),(0,-.80,1.35),(-.55,-.62,1.35),(.55,-.62,1.35)]
for t in targets:
    vi=min(range(len(o.data.vertices)),key=lambda i:(o.data.vertices[i].co-Vector(t)).length)
    vals=[]
    for p in o.data.polygons:
        for li in p.loop_indices:
            if o.data.loops[li].vertex_index==vi: vals.append(tuple(round(v,4) for v in uv[li].uv))
    print('TARGET',t,'VERT',tuple(round(v,3) for v in o.data.vertices[vi].co),'UV',vals[:4])

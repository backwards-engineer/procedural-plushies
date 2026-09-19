import bpy
import math
import os
from mathutils import Vector


OUT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(OUT_DIR, "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


CHARACTERS = [
    dict(name="Burplepup", body=(0.82, 0.86, 0.92, 1), accent=(0.05, 0.25, 0.68, 1), kind="dog"),
    dict(name="Sparkit", body=(1.00, 0.66, 0.05, 1), accent=(0.20, 0.12, 0.04, 1), kind="electric"),
    dict(name="Leafin", body=(0.42, 0.67, 0.13, 1), accent=(0.16, 0.42, 0.06, 1), kind="leaf"),
    dict(name="Flambo", body=(0.93, 0.28, 0.12, 1), accent=(1.00, 0.66, 0.05, 1), kind="bird"),
    dict(name="Aquari", body=(0.08, 0.48, 0.78, 1), accent=(0.25, 0.78, 0.86, 1), kind="fish"),
    dict(name="Duskit", body=(0.25, 0.12, 0.31, 1), accent=(0.62, 0.34, 0.73, 1), kind="cat"),
    dict(name="Pandooze", body=(0.88, 0.82, 0.70, 1), accent=(0.08, 0.06, 0.05, 1), kind="panda"),
    dict(name="Bloomi", body=(0.75, 0.48, 0.27, 1), accent=(0.95, 0.25, 0.43, 1), kind="flower"),
    dict(name="Zappu", body=(0.07, 0.42, 0.43, 1), accent=(0.96, 0.67, 0.08, 1), kind="dragon"),
    dict(name="Chonko", body=(0.72, 0.32, 0.10, 1), accent=(0.94, 0.65, 0.32, 1), kind="hamster"),
]


def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.armatures, bpy.data.materials):
        pass


def mat(name, color, roughness=0.82):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.diffuse_color = color
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
    return m


MATS = {}


def material(name, color):
    key = name + str(color)
    if key not in MATS:
        MATS[key] = mat(name, color)
    return MATS[key]


def make_face_texture(name, body_color, patch_style=None):
    """Create an opaque, fully baked head base-color texture for FBX/Unreal."""
    size = 512
    img = bpy.data.images.new(name + '_FaceTexture', width=size, height=size, alpha=True)
    # Bake the body color into the bitmap. FBX cannot reproduce Blender shader mixes.
    px = list(body_color) * (size * size)

    def ellipse(cx, cy, rx, ry, color):
        x0=max(0,int(cx-rx)); x1=min(size,int(cx+rx)+1)
        y0=max(0,int(cy-ry)); y1=min(size,int(cy+ry)+1)
        for y in range(y0,y1):
            dy=(y-cy)/ry
            for x in range(x0,x1):
                dx=(x-cx)/rx
                if dx*dx+dy*dy <= 1:
                    i=(y*size+x)*4
                    px[i:i+4]=color

    # Atlas placement is tuned for the front-facing quadrant of Blender's UV sphere.
    # Vertical dimensions are deliberately stretched to counter spherical UV compression.
    # It contains eye whites/irises, muzzle, nose, cheeks and optional markings.
    if patch_style == 'dog':
        ellipse(91, 326, 39, 88, (0.05,0.25,0.68,1))
    elif patch_style == 'panda':
        ellipse(91, 330, 31, 70, (0.03,0.02,0.015,1)); ellipse(165,330,31,70,(0.03,0.02,0.015,1))
    muzzle=(0.90,0.76,0.58,1)
    ellipse(128,238,55,52,muzzle)
    for cx in (94,162):
        ellipse(cx,338,21,45,(0.015,0.010,0.008,1))
        ellipse(cx-5,354,6,12,(1,1,1,1))
    ellipse(128,258,14,15,(0.035,0.018,0.012,1))
    ellipse(65,250,18,16,(1.0,0.30,0.35,0.9)); ellipse(191,250,18,16,(1.0,0.30,0.35,0.9))
    if patch_style == 'moon': ellipse(128,422,18,27,(0.95,0.78,0.25,1))
    img.pixels.foreach_set(px)
    img.filepath_raw=os.path.join(EXPORT_DIR,name+'_Face.png')
    img.file_format='PNG'
    img.save()
    img.pack()
    return img


def face_material(name, body_color, patch_style=None):
    m=bpy.data.materials.new(name+'_FaceMat')
    m.use_nodes=True
    nodes=m.node_tree.nodes; links=m.node_tree.links
    nodes.clear()
    out=nodes.new('ShaderNodeOutputMaterial')
    bsdf=nodes.new('ShaderNodeBsdfPrincipled')
    tex=nodes.new('ShaderNodeTexImage'); tex.image=make_face_texture(name,body_color,patch_style)
    # Direct Image Texture -> Base Color is intentionally simple and FBX-compatible.
    links.new(tex.outputs['Color'],bsdf.inputs['Base Color']); links.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value=.82
    return m


def assign_face_material(head, face_mat):
    """Use one baked material over the entire head—no unsupported shader layering."""
    head.data.materials.clear()
    head.data.materials.append(face_mat)
    for poly in head.data.polygons:
        poly.material_index=0


def smooth(obj):
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True


def add_uv(name, loc, scale, material_obj, bone, segments=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material_obj)
    smooth(o)
    o["deform_bone"] = bone
    return o


def add_cone(name, loc, radius1, radius2, depth, material_obj, bone, rotation=(0,0,0), vertices=16):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material_obj)
    smooth(o)
    bevel = o.modifiers.new('Soft_Edges', 'BEVEL')
    bevel.width = 0.06
    bevel.segments = 1
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    o["deform_bone"] = bone
    return o


def add_eye(parts, prefix, x, z, bone='head'):
    black = material('Black', (0.012, 0.008, 0.006, 1))
    white = material('EyeHighlight', (1, 1, 1, 1))
    parts.append(add_uv(prefix + '_Eye', (x, -0.865, z), (0.145, 0.055, 0.18), black, bone, 16, 10))
    parts.append(add_uv(prefix + '_Glint', (x - 0.035 if x > 0 else x + 0.035, -0.922, z + 0.055), (0.035, 0.018, 0.045), white, bone, 12, 8))


def add_ear(parts, side, color, style='round'):
    x = 0.62 * side
    if style == 'point':
        o = add_cone(('Ear_L' if side < 0 else 'Ear_R'), (x, 0, 2.18), .31, .04, .72, color,
                     'ear_l' if side < 0 else 'ear_r', rotation=(0, 0, -0.18 * side))
    elif style == 'long':
        o = add_uv(('Ear_L' if side < 0 else 'Ear_R'), (x, 0, 2.32), (.25, .24, .62), color,
                   'ear_l' if side < 0 else 'ear_r')
        o.rotation_euler.y = 0.22 * side
    else:
        o = add_uv(('Ear_L' if side < 0 else 'Ear_R'), (x, 0, 2.05), (.32, .25, .36), color,
                   'ear_l' if side < 0 else 'ear_r')
    parts.append(o)


def make_armature(name):
    data = bpy.data.armatures.new(name + '_Skeleton')
    arm = bpy.data.objects.new(name + '_Armature', data)
    bpy.context.collection.objects.link(arm)
    arm.show_in_front = True
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    def bone(n, head, tail, parent=None):
        b = data.edit_bones.new(n)
        b.head, b.tail = head, tail
        if parent:
            b.parent = data.edit_bones.get(parent)
        return b

    bone('root', (0,0,0), (0,0,.35))
    bone('body', (0,0,.35), (0,0,1.15), 'root')
    bone('head', (0,0,1.05), (0,0,1.85), 'body')
    bone('arm_l', (-.48,0,1.0), (-1.05,0,.82), 'body')
    bone('arm_r', (.48,0,1.0), (1.05,0,.82), 'body')
    bone('leg_l', (-.30,0,.45), (-.53,0,.02), 'body')
    bone('leg_r', (.30,0,.45), (.53,0,.02), 'body')
    # Identical superset on every character so all FBXs can share one UE Skeleton.
    bone('ear_l',(-.48,0,1.95),(-.72,0,2.45),'head')
    bone('ear_r',(.48,0,1.95),(.72,0,2.45),'head')
    bone('tail',(0,.45,.78),(0,1.10,.85),'body')
    bone('head_accessory',(0,0,2.0),(0,0,2.6),'head')
    bone('back_accessory',(0,.45,1.0),(0,.9,1.5),'body')
    bpy.ops.object.mode_set(mode='OBJECT')
    arm.data.display_type = 'STICK'
    return arm


def bind_parts(parts, arm):
    for o in parts:
        bone_name = o.get('deform_bone', 'body')
        vg = o.vertex_groups.new(name=bone_name)
        vg.add(range(len(o.data.vertices)), 1.0, 'REPLACE')
        mod = o.modifiers.new('Armature', 'ARMATURE')
        mod.object = arm
        o.parent = arm
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = arm.name.replace('_Armature', '_SK')
    return mesh


def build_character(cfg, x_offset):
    name, kind = cfg['name'], cfg['kind']
    body_m = material(name + '_Body', cfg['body'])
    accent = material(name + '_Accent', cfg['accent'])
    cream = material('Cream', (0.86, 0.72, 0.53, 1))
    parts = []

    parts.append(add_uv('Body', (0,0,0.92), (.82,.72,.82), body_m, 'body'))
    head=add_uv('Head', (0,-.02,1.55), (.86,.78,.82), body_m, 'head')
    patch_style={'dog':'dog','panda':'panda','cat':'moon'}.get(kind)
    assign_face_material(head,face_material(name,cfg['body'],patch_style))
    parts.append(head)
    parts.append(add_uv('Arm_L', (-.82,-.02,.94), (.28,.26,.46), body_m, 'arm_l'))
    parts[-1].rotation_euler.y = -.48
    parts.append(add_uv('Arm_R', (.82,-.02,.94), (.28,.26,.46), body_m, 'arm_r'))
    parts[-1].rotation_euler.y = .48
    parts.append(add_uv('Leg_L', (-.39,-.11,.31), (.38,.40,.31), accent, 'leg_l'))
    parts.append(add_uv('Leg_R', (.39,-.11,.31), (.38,.40,.31), accent, 'leg_r'))

    if kind == 'dog':
        add_ear(parts, -1, accent, 'long'); add_ear(parts, 1, accent, 'long')
    elif kind == 'electric':
        add_ear(parts, -1, accent, 'long'); add_ear(parts, 1, accent, 'long')
        bolt = add_cone('Tail', (0,.88,.78), .25,.06,.8, accent,'tail', rotation=(math.pi/2,0,0)); parts.append(bolt)
    elif kind == 'leaf':
        leaf = add_uv('HeadLeaf', (.15,0,2.36), (.30,.12,.58), accent,'head_accessory'); leaf.rotation_euler.y=.48; parts.append(leaf)
        parts.append(add_uv('Tail', (0,.88,.76), (.18,.44,.18), accent,'tail'))
    elif kind == 'bird':
        for i, sc in enumerate((.42,.34,.26)):
            parts.append(add_cone('Crest'+str(i),(0,.02,2.18+i*.12),sc*.5,.03,sc*1.4,accent,'head_accessory',rotation=(0.15,0.3,0)))
        parts.append(add_cone('Beak',(0,-.98,1.38),.22,.02,.35,accent,'head',rotation=(math.pi/2,0,0)))
        parts.append(add_uv('Tail',(0,.90,.72),(.20,.48,.22),accent,'tail'))
    elif kind == 'fish':
        for side in (-1,1):
            # Mirrored rotations keep both fin points facing outward.
            parts.append(add_cone('Fin_L' if side<0 else 'Fin_R',(side*.82,.02,1.62),.38,.03,.62,accent,'ear_l' if side<0 else 'ear_r',rotation=(0,side*math.pi/2,0)))
        parts.append(add_cone('Tail',(0,1.02,.82),.45,.05,.75,accent,'tail',rotation=(math.pi/2,0,0)))
    elif kind == 'cat':
        add_ear(parts,-1,accent,'point'); add_ear(parts,1,accent,'point')
        parts.append(add_uv('Tail',(0,.92,.80),(.18,.45,.18),accent,'tail'))
    elif kind == 'panda':
        add_ear(parts,-1,accent,'round'); add_ear(parts,1,accent,'round')
    elif kind == 'flower':
        for i in range(9):
            a=2*math.pi*i/9
            p=add_uv('Petal_%02d'%i,(math.cos(a)*.62,-.01,1.77+math.sin(a)*.62),(.28,.20,.43),accent,'head_accessory',16,10)
            p.rotation_euler.y=a+math.pi/2; parts.append(p)
        parts.append(add_uv('BellyLeaf', (0,-.73,.72),(.47,.055,.35),material('LeafGreen',(0.18,.48,.12,1)),'body'))
    elif kind == 'dragon':
        add_ear(parts,-1,accent,'point'); add_ear(parts,1,accent,'point')
        parts.append(add_cone('Tail',(0,1.0,.78),.34,.04,.78,accent,'tail',rotation=(math.pi/2,0,0)))
        for i in range(3): parts.append(add_cone('BackSpike'+str(i),(0,.58,1.0+i*.28),.18,.02,.38,accent,'back_accessory',rotation=(math.pi/2,0,0)))
        parts.append(add_uv('BellyBolt',(0,-.73,.83),(.24,.045,.42),accent,'body'))
    elif kind == 'hamster':
        add_ear(parts,-1,accent,'round'); add_ear(parts,1,accent,'round')
        parts.append(add_uv('Belly',(0,-.70,.87),(.53,.055,.58),cream,'body'))
        parts.append(add_uv('HeadStripe',(0,-.77,1.91),(.22,.045,.28),accent,'head'))

    arm = make_armature(name)
    mesh = bind_parts(parts, arm)
    arm.location.x = x_offset
    arm["unreal_asset_name"] = 'SK_' + name
    arm["ragdoll_note"] = 'Create Physics Asset on FBX import; capsules map to named deform bones.'
    mesh["character"] = name
    return arm, mesh


def export_character(name, arm, mesh):
    saved_loc=arm.location.copy()
    arm.location=(0,0,0)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True); mesh.select_set(True)
    bpy.context.view_layer.objects.active = arm
    path = os.path.join(EXPORT_DIR, 'SK_' + name + '.fbx')
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={'ARMATURE','MESH'},
        apply_scale_options='FBX_SCALE_UNITS', add_leaf_bones=False,
        bake_anim=False, mesh_smooth_type='FACE', use_armature_deform_only=True,
        axis_forward='-Y', axis_up='Z', path_mode='COPY', embed_textures=True
    )
    arm.location=saved_loc
    bpy.context.view_layer.update()


def main():
    clean_scene()
    built=[]
    for i,cfg in enumerate(CHARACTERS):
        arm,mesh=build_character(cfg,(i-4.5)*2.7)
        built.append((cfg['name'],arm,mesh))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,'PlushieCollection.blend'))
    for name,arm,mesh in built:
        export_character(name,arm,mesh)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,'PlushieCollection.blend'))
    print('CREATED', len(built), 'RIGGED PLUSHIES')


if __name__ == '__main__':
    main()

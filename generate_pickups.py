import bpy
import math
import os
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,'pickup_exports')
os.makedirs(OUT,exist_ok=True)


def clean():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)


def mat(name,color,metallic=0.0,roughness=.25,alpha=1.0,emission=None):
    m=bpy.data.materials.get(name)
    if m:return m
    m=bpy.data.materials.new(name); m.use_nodes=True
    m.diffuse_color=(*color[:3],alpha)
    b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*color[:3],1)
    b.inputs['Metallic'].default_value=metallic
    b.inputs['Roughness'].default_value=roughness
    b.inputs['Alpha'].default_value=alpha
    if emission:
        b.inputs['Emission Color'].default_value=(*emission[:3],1)
        b.inputs['Emission Strength'].default_value=2.5
    if alpha<1:
        m.surface_render_method='DITHERED'
        m.use_transparency_overlap=False
    m['UE_BlendMode']='Translucent' if alpha<1 else 'Opaque'
    m['UE_Metallic']=metallic; m['UE_Roughness']=roughness
    return m


def baked_icon_material(name,bg,kind,metallic=.45,roughness=.12):
    """Opaque base-color bitmap; survives Blender -> FBX -> Unreal without node translation."""
    size=512
    img=bpy.data.images.new(name+'_Texture',width=size,height=size,alpha=True)
    px=list((*bg[:3],1.0))*(size*size)

    def ellipse(cx,cy,rx,ry,c):
        for y in range(max(0,int(cy-ry)),min(size,int(cy+ry)+1)):
            for x in range(max(0,int(cx-rx)),min(size,int(cx+rx)+1)):
                if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1:
                    i=(y*size+x)*4; px[i:i+4]=c

    def rect(x0,y0,x1,y1,c):
        for y in range(max(0,y0),min(size,y1)):
            for x in range(max(0,x0),min(size,x1)):
                i=(y*size+x)*4; px[i:i+4]=c

    def thick_line(x0,y0,x1,y1,width,c):
        steps=max(abs(x1-x0),abs(y1-y0),1)
        for s in range(steps+1):
            t=s/steps; x=x0+(x1-x0)*t; y=y0+(y1-y0)*t
            ellipse(x,y,width,width,c)

    def polygon(points,c):
        minx=max(0,int(min(p[0] for p in points))); maxx=min(size-1,int(max(p[0] for p in points)))
        miny=max(0,int(min(p[1] for p in points))); maxy=min(size-1,int(max(p[1] for p in points)))
        for y in range(miny,maxy+1):
            for x in range(minx,maxx+1):
                inside=False; j=len(points)-1
                for i,p in enumerate(points):
                    q=points[j]
                    if ((p[1]>y)!=(q[1]>y)) and x < (q[0]-p[0])*(y-p[1])/(q[1]-p[1]+1e-9)+p[0]:inside=not inside
                    j=i
                if inside:
                    k=(y*size+x)*4; px[k:k+4]=c

    white=(.92,.90,.82,1); dark=(.012,.01,.008,1); gray=(.36,.40,.44,1)
    if kind=='skull':
        # Crossbones sit behind a compact skull in the front UV quadrant (U≈0.25).
        thick_line(86,210,170,330,7,white); thick_line(86,330,170,210,7,white)
        for x,y in ((82,205),(174,335),(82,335),(174,205)):ellipse(x,y,10,14,white)
        ellipse(128,320,43,58,white); rect(105,248,151,306,white)
        ellipse(113,330,9,16,dark); ellipse(143,330,9,16,dark)
        polygon([(128,312),(121,292),(135,292)],dark)
        for x in (112,128,144):rect(x-4,250,x+4,280,dark)
    elif kind=='star':
        pts=[]
        for i in range(10):
            a=math.pi/2+math.pi*i/5; r=1 if i%2==0 else .43
            pts.append((128+58*r*math.cos(a),300+94*r*math.sin(a)))
        polygon(pts,white)
    elif kind=='kg':
        rect(78,205,178,370,gray)
        # Block-letter K
        thick_line(101,230,101,345,6,dark); thick_line(101,288,126,345,6,dark); thick_line(101,288,126,230,6,dark)
        # Block-letter G
        thick_line(158,345,132,345,6,dark); thick_line(132,345,132,230,6,dark); thick_line(132,230,158,230,6,dark)
        thick_line(158,230,158,288,6,dark); thick_line(146,288,162,288,6,dark)

    img.pixels.foreach_set(px); img.filepath_raw=os.path.join(OUT,name+'.png'); img.file_format='PNG'; img.save(); img.pack()
    m=bpy.data.materials.new(name); m.use_nodes=True
    nodes=m.node_tree.nodes; links=m.node_tree.links; nodes.clear()
    out=nodes.new('ShaderNodeOutputMaterial'); bsdf=nodes.new('ShaderNodeBsdfPrincipled'); tex=nodes.new('ShaderNodeTexImage'); tex.image=img
    bsdf.inputs['Metallic'].default_value=metallic; bsdf.inputs['Roughness'].default_value=roughness
    links.new(tex.outputs['Color'],bsdf.inputs['Base Color']); links.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return m


BLACK=mat('M_BlackGloss',(0.008,.01,.014),.25,.12)
WHITE=mat('M_White',(0.9,.9,.86),.05,.25)
SILVER=mat('M_Silver',(.45,.5,.56),.9,.12)
GOLD=mat('M_Gold',(1.0,.48,.035),.92,.10)
RED=mat('M_Red',(.75,.015,.02),.55,.12)
BLUE=mat('M_Blue',(.02,.18,.70),.55,.12)
GREEN=mat('M_Green',(.08,.62,.16),.35,.14)
PURPLE=mat('M_Purple',(.43,.04,.72),.45,.10)
YELLOW=mat('M_Yellow',(1.0,.73,.03),.45,.12)
PINK=mat('M_Pink',(1.0,.12,.52),.35,.10)
ORANGE=mat('M_Orange',(1.0,.24,.02),.45,.12)
GLASS=mat('M_Glass_Clear',(.28,.60,.95),.05,.05,.22)
GLASS_GREEN=mat('M_Glass_Green',(.20,1.0,.22),.08,.06,.28)
GLASS_PURPLE=mat('M_Glass_Purple',(.72,.12,1.0),.10,.05,.30)


def finish(o,name,material,bone=None):
    o.name=name
    if o.type=='MESH':
        o.data.materials.append(material)
        for p in o.data.polygons:p.use_smooth=True
    return o


def sphere(parts,name,loc,scale,material,segments=20,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc)
    o=finish(bpy.context.object,name,material); o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); parts.append(o); return o


def ico(parts,name,loc,scale,material,subdiv=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv,location=loc)
    o=finish(bpy.context.object,name,material); o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); parts.append(o); return o


def cylinder(parts,name,loc,radius,depth,material,rotation=(0,0,0),vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rotation)
    o=finish(bpy.context.object,name,material); parts.append(o); return o


def cube(parts,name,loc,scale,material,bevel=.05,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rotation)
    o=finish(bpy.context.object,name,material); o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('SoftEdges','BEVEL'); mod.width=bevel; mod.segments=1
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    parts.append(o); return o


def cone(parts,name,loc,r1,r2,depth,material,rotation=(0,0,0),vertices=16):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r1,radius2=r2,depth=depth,location=loc,rotation=rotation)
    o=finish(bpy.context.object,name,material); parts.append(o); return o


def torus(parts,name,loc,major,minor,material,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=20,minor_segments=8,location=loc,rotation=rotation)
    o=finish(bpy.context.object,name,material); parts.append(o); return o


def curve_tube(parts,name,points,radius,material,cyclic=False):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=radius; cu.bevel_resolution=1; cu.resolution_u=4
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for bp,co in zip(sp.bezier_points,points):bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    sp.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); cu.materials.append(material)
    bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.convert(target='MESH')
    parts.append(o); return o


def text_obj(parts,name,text,loc,size,material,extrude=.025,rotation=(math.pi/2,0,0)):
    bpy.ops.object.text_add(location=loc,rotation=rotation)
    o=bpy.context.object; o.name=name; o.data.body=text; o.data.align_x='CENTER'; o.data.align_y='CENTER'
    o.data.size=size; o.data.extrude=extrude; o.data.bevel_depth=.006; o.data.resolution_u=3; o.data.bevel_resolution=1; o.data.materials.append(material)
    bpy.context.view_layer.objects.active=o; bpy.ops.object.convert(target='MESH'); parts.append(o); return o


def star(parts,name,loc,r_outer,r_inner,depth,material,rotation=(math.pi/2,0,0)):
    verts=[]
    for z in (-depth/2,depth/2):
        for i in range(10):
            a=math.pi/2+math.pi*i/5; r=r_outer if i%2==0 else r_inner
            verts.append((r*math.cos(a),r*math.sin(a),z))
    faces=[]
    faces.append(tuple(range(10))); faces.append(tuple(range(10,20)))
    for i in range(10):faces.append((i,(i+1)%10,(i+1)%10+10,i+10))
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.materials.append(material)
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rotation
    parts.append(o); return o


def coins(parts,count,color=GOLD,zbase=.28):
    for i in range(count):
        # Deterministic layered spiral keeps larger rarities readable without dense geometry.
        a=2.399963*i; layer=i//8; r=.12+.10*(i%7)
        cylinder(parts,'Coin_%02d'%i,(math.cos(a)*min(r,.64),math.sin(a)*min(r,.64),zbase+layer*.12+(i%3)*.035),.13,.045,color,rotation=(math.pi/2,.23*i,0),vertices=12)


def capsule(parts,base_mat,contents=7,glass=GLASS):
    sphere(parts,'GlassShell',(0,0,1.0),(1,1,1),glass)
    sphere(parts,'LowerShell',(0,0,.68),(1.01,1.01,.68),base_mat)
    torus(parts,'Seam',(0,0,1.0),.94,.045,base_mat)
    # Contents sit in the visible upper chamber instead of inside the opaque bowl.
    coins(parts,contents,GOLD,1.18)


def bomb(parts,mega=False):
    bg=(.75,.015,.02) if mega else (.008,.01,.014)
    m=baked_icon_material('M_MegaBomb_Skull' if mega else 'M_Bomb_Skull',bg,'skull',.55 if mega else .25,.12)
    sphere(parts,'BombBody',(0,0,1.0),(1,1,1),m)
    cylinder(parts,'FuseSocket',(0,0,2.0),.25,.32,BLACK)
    curve_tube(parts,'Fuse',[(0,0,2.15),(.02,0,2.45),(.22,0,2.72)],.085,BLACK)


def magnet(parts):
    # One continuous rectangular-section U mesh. Materials split along its path.
    path=[(-.62,1.98),(-.62,1.68),(-.62,.78)]
    for i in range(1,10):
        a=math.pi+math.pi*i/10; path.append((.62*math.cos(a),.78+.62*math.sin(a)))
    path += [(.62,.78),(.62,1.68),(.62,1.98)]
    width=.42; depth=.48; verts=[]
    for i,p in enumerate(path):
        prev=Vector(path[max(0,i-1)]); nxt=Vector(path[min(len(path)-1,i+1)])
        tangent=(nxt-prev).normalized(); normal=Vector((-tangent.y,tangent.x))
        a=Vector(p)+normal*width/2; b=Vector(p)-normal*width/2
        verts += [(a.x,-depth/2,a.y),(b.x,-depth/2,b.y),(a.x,depth/2,a.y),(b.x,depth/2,b.y)]
    faces=[]; mats=[]
    for i in range(len(path)-1):
        q=i*4; n=q+4
        faces += [(q,n,n+1,q+1),(q+2,q+3,n+3,n+2),(q,q+2,n+2,n),(q+1,n+1,n+3,q+3)]
        midx=(path[i][0]+path[i+1][0])/2
        mi=2 if i in (0,len(path)-2) else (1 if midx<0 else 0)
        mats += [mi]*4
    faces += [(0,1,3,2),(len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3)]; mats += [2,2]
    me=bpy.data.meshes.new('MagnetU'); me.from_pydata(verts,[],faces); me.materials.append(RED); me.materials.append(BLUE); me.materials.append(SILVER)
    for p,mi in zip(me.polygons,mats):p.material_index=mi
    o=bpy.data.objects.new('MagnetU',me); bpy.context.collection.objects.link(o)
    mod=o.modifiers.new('EdgeSoftening','BEVEL'); mod.width=.035; mod.segments=1
    bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); parts.append(o)


def crown(parts,scale=1.0,z=1.0):
    torus(parts,'CrownBand',(0,-.74,z),.38*scale,.09*scale,GOLD,rotation=(math.pi/2,0,0))
    for i,x in enumerate((-.30,-.15,0,.15,.30)):
        cone(parts,'CrownPoint'+str(i),(x*scale,-.76,z+.28*scale),.09*scale,.015*scale,.48*scale,GOLD)
        sphere(parts,'CrownGem'+str(i),(x*scale,-.77,z+.53*scale),(.05,.03,.05),PINK,12,8)


def bear(parts,golden=False,mystery=False,mini=False,faces=True):
    s=.48 if mini else 1.0; base=GOLD if golden else (mat('M_MysteryPlush',(.035,.022,.055),.05,.72) if mystery else mat('M_MiniGreen',(.20,.72,.18),.05,.65))
    seg=16 if mini else 20; rings=8 if mini else 12
    sphere(parts,'BearBody',(0,0,.75*s),(.64*s,.55*s,.70*s),base,seg,rings)
    sphere(parts,'BearHead',(0,-.02,1.40*s),(.70*s,.64*s,.62*s),base,seg,rings)
    sphere(parts,'EarL',(-.48*s,0,1.82*s),(.22*s,.18*s,.23*s),base,seg,rings); sphere(parts,'EarR',(.48*s,0,1.82*s),(.22*s,.18*s,.23*s),base,seg,rings)
    sphere(parts,'FootL',(-.34*s,-.15,.22*s),(.30*s,.32*s,.22*s),base,seg,rings); sphere(parts,'FootR',(.34*s,-.15,.22*s),(.30*s,.32*s,.22*s),base,seg,rings)
    if faces:
        sphere(parts,'EyeL',(-.23*s,-.62*s,1.46*s),(.075*s,.035*s,.10*s),BLACK,16,10); sphere(parts,'EyeR',(.23*s,-.62*s,1.46*s),(.075*s,.035*s,.10*s),BLACK,16,10)
        sphere(parts,'Muzzle',(0,-.61*s,1.25*s),(.28*s,.05*s,.18*s),WHITE,20,12)


def build(name,kind,index):
    parts=[]
    if kind.startswith('capsule_'):
        colors={'common':SILVER,'uncommon':BLUE,'rare':PURPLE,'epic':RED,'golden':GOLD}
        rarity=kind.split('_')[1]
        counts={'common':3,'uncommon':7,'rare':12,'epic':18,'golden':25}
        capsule(parts,colors[rarity],counts[rarity])
    elif kind=='bomb':bomb(parts,False)
    elif kind=='mega_bomb':bomb(parts,True)
    elif kind=='magnet':magnet(parts)
    elif kind=='ticket':
        capsule(parts,GREEN,0,GLASS_GREEN); cube(parts,'Ticket',(0,-.52,1.46),(.48,.035,.25),YELLOW,.07,rotation=(0,0,-.10)); text_obj(parts,'TicketText','TICKET',(0,-.575,1.45),.16,BLACK,.01)
    elif kind=='jackpot':
        sphere(parts,'RainbowGlass',(0,0,1),(1,1,1),mat('M_RainbowGlass',(.55,.12,.95),.35,.04,.32)); crown(parts,.95,1.02)
    elif kind=='gold_plush':bear(parts,golden=True,faces=False)
    elif kind=='rainbow':
        colors=(RED,ORANGE,YELLOW,GREEN,BLUE,PURPLE,PINK)
        rb=ico(parts,'RainbowSphere',(0,0,1),(1,1,1),colors[0],3)
        for c in colors[1:]:rb.data.materials.append(c)
        # Faceted chromatic patches survive FBX better than a procedural iridescent shader.
        for p in rb.data.polygons:
            a=(math.atan2(p.center.y,p.center.x)+math.pi)/(2*math.pi)
            p.material_index=(int(a*7)+int((p.center.z+1)*3))%7
    elif kind=='sticky':
        slime=mat('M_Slime',(.18,.78,.06),.05,.18)
        sphere(parts,'StickyGlass',(0,0,1),(1,1,1),mat('M_StickyGlass',(.65,1,.05),.05,.12,.38)); sphere(parts,'StickyCap',(0,0,1.60),(1.01,1.01,.42),YELLOW)
        torus(parts,'SlimeBand',(0,0,.62),.86,.11,slime)
        bear(parts,mini=True,faces=False)
        for i,(x,y,length) in enumerate(((-.72,-.15,.26),(-.38,-.55,.40),(0,-.72,.31),(.38,-.55,.46),(.72,-.12,.24))):
            cone(parts,'SlimeNeck'+str(i),(x,y,.62-length/2),.065,.14,length,slime,vertices=12)
            sphere(parts,'SlimeDrop'+str(i),(x,y,.61-length),(.12,.12,.15),slime,16,8)
    elif kind=='heavy':
        sphere(parts,'HeavySphere',(0,0,1),(1,1,1),baked_icon_material('M_Heavy_KG',(.025,.025,.028),'kg',.9,.28))
    elif kind=='bouncy':
        sphere(parts,'BouncyBall',(0,0,1),(1,1,1),baked_icon_material('M_Bouncy_Star',(.75,.015,.02),'star',.55,.12))
    elif kind=='crystal':
        ico(parts,'CrystalCapsule',(0,0,1),(1,1,1),mat('M_Crystal',(.08,.35,1.0),.28,.04,.50),2)
        ico(parts,'CrystalCore',(0,0,1),(.66,.66,.66),mat('M_CrystalCore',(.12,.55,1),.55,.07,1,(.05,.25,1)),2)
    elif kind=='dupe':
        capsule(parts,PURPLE,0,GLASS_PURPLE)
        for x in (-.35,.35):
            sphere(parts,'MiniHead',(x,-.18,1.28),(.32,.28,.30),PINK,16,8); sphere(parts,'MiniEarL',(x-.21,-.16,1.51),(.11,.09,.12),PURPLE,12,8); sphere(parts,'MiniEarR',(x+.21,-.16,1.51),(.11,.09,.12),PURPLE,12,8)
            sphere(parts,'MiniEyeL',(x-.10,-.45,1.30),(.035,.02,.05),BLACK,12,8); sphere(parts,'MiniEyeR',(x+.10,-.45,1.30),(.035,.02,.05),BLACK,12,8)
    elif kind=='mystery_plush':bear(parts,mystery=True,faces=False)
    elif kind=='mystery_capsule':
        sphere(parts,'MysteryCapsule',(0,0,1),(1,1,1),mat('M_MysteryCapsule',(.13,.04,.35),.35,.07,.50)); text_obj(parts,'Question','?',(0,-.20,1.04),.85,mat('M_QuestionGlow',(.72,.25,1),.1,.12,1,(.4,.05,1)),.025)
    elif kind=='coin':
        cylinder(parts,'CoinCore',(0,0,.07),.44,.14,GOLD,vertices=24)
        torus(parts,'CoinRimTop',(0,0,.105),.36,.035,GOLD)
        torus(parts,'CoinRimBottom',(0,0,.035),.36,.035,GOLD)

    # Collapse each pickup to one static mesh while preserving its material slots.
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join()
    asset=bpy.context.object; asset.name='SM_'+name
    bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    asset['UE_StaticMesh']=True; asset['UE_OriginVerified']='0,0,0'
    asset.location.x=(index-9)*2.75
    return asset


ITEMS=[
 ('CommonCapsule','capsule_common'),('UncommonCapsule','capsule_uncommon'),('RareCapsule','capsule_rare'),('EpicCapsule','capsule_epic'),('GoldenCapsule','capsule_golden'),
 ('Bomb','bomb'),('MegaBomb','mega_bomb'),('Magnet','magnet'),('TicketCapsule','ticket'),('JackpotSphere','jackpot'),
 ('GoldenPlush','gold_plush'),('RainbowSphere','rainbow'),('StickyCapsule','sticky'),('HeavySphere','heavy'),('BouncyBall','bouncy'),('CrystalCapsule','crystal'),('DupeCapsule','dupe'),('MysteryPlush','mystery_plush'),('MysteryCapsule','mystery_capsule'),('Coin','coin')]


def main():
    clean(); assets=[]
    for i,(name,kind) in enumerate(ITEMS):assets.append(build(name,kind,i))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'PickupCollection.blend'))
    for asset in assets:
        saved=asset.location.copy(); asset.location=(0,0,0); bpy.context.view_layer.update()
        bpy.ops.object.select_all(action='DESELECT'); asset.select_set(True); bpy.context.view_layer.objects.active=asset
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,asset.name+'.fbx'),use_selection=True,object_types={'MESH'},apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,axis_forward='-Y',axis_up='Z')
        asset.location=saved
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'PickupCollection.blend'))
    print('CREATED',len(assets),'STATIC PICKUPS INCLUDING STANDALONE COIN')


if __name__=='__main__':main()

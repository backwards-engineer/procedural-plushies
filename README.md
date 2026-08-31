# Spherical Plushie Collection

`PlushieCollection.blend` contains ten stylized plush characters based on the supplied concept image. Each character has its own armature and joined skeletal mesh.

## Unreal import

Import an `exports/SK_*.fbx` with **Skeletal Mesh** enabled, **Import Animations** disabled, and **Create Physics Asset** enabled. In the generated Physics Asset, use spheres for `body` and `head`, capsules for arms/legs, and small capsules or boxes for ears, tails, fins, petals, and crests. Delete collision bodies for tiny decorative geometry if Unreal generates any.

Every character exports with the same hierarchy and reference pose: `root`, `body`, `head`, `arm_l`, `arm_r`, `leg_l`, `leg_r`, `ear_l`, `ear_r`, `tail`, `head_accessory`, and `back_accessory`. This allows all ten assets to share one Unreal Skeleton. Mesh components use rigid 100% weights to keep the intentionally toy-like shapes stable during ragdoll simulation.

The plush collection uses reduced-resolution, smooth-shaded geometry: 20×12 main spheres, 16-sided cones, single-segment bevels, and 16×10 flower petals. This substantially reduces skeletal-mesh polygon counts while preserving the shared rig, UV face textures, and rounded silhouette.

For the first FBX, leave **Skeleton** set to **None** so Unreal creates `SKEL_Plushies`. For each later FBX, select that same skeleton. If Unreal reports a conflict with an earlier version, delete/reimport the old skeletal mesh and skeleton or import these revised files into a new folder; Unreal caches the previously imported hierarchy. Do not select the UE mannequin skeleton.

All FBXs are exported at world origin even though the master Blender scene displays the characters as a lineup. Face PNGs in `exports/` are opaque, fully baked head base-color textures rather than separate eye, muzzle, cheek, or nose geometry. They are also embedded in each FBX.

The face atlases include vertical UV compensation so the eyes, muzzle, cheeks, markings, and forehead symbols retain their intended proportions after mapping onto the spherical heads and importing into Unreal.

In Unreal's FBX import dialog enable **Import Materials** and **Import Textures**. Each head material uses the most portable FBX graph possible: one image texture wired directly to Base Color. If Unreal retained a material from an older import, enable **Material Import Method: Create New Materials** or delete that old material before reimporting.

## Regeneration

Run Blender in background mode:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python .\generate_plushies.py
```

The script overwrites `PlushieCollection.blend` and the individual FBX exports.

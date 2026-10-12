# Static pickup import into Unreal

Import each `pickup_exports/SM_*.fbx` as a Static Mesh. Every exported object origin is `(0,0,0)` at the bottom-center of the pickup.

`SM_Coin.fbx` is the standalone version of the low-poly gold coin used inside the rarity capsules. Capsule contents scale from 3 coins in Common to 25 coins in Golden.

The bomb skull-and-crossbones, bouncy-ball star, and Heavy Sphere `KG` label are baked opaque PNG base-color textures. They are embedded in their FBXs and also saved alongside the exports.

The collection uses reduced-resolution, smooth-shaded geometry: 20×12 primary spheres, 20×8 toruses, 12-sided capsule coins, low-resolution curves/text, and a 320-face rainbow sphere. Each final FBX is kept below 2,500 polygons.

Recommended options: **Import Materials**, **Import Textures**, **Combine Meshes**, **Generate Missing Collision**, and **Convert Scene Unit**. The generated materials contain explicit Base Color, Metallic, Roughness, Alpha, and Emission values.

FBX cannot set Unreal-specific material blend modes. For `M_Glass_Clear`, `M_Glass_Green`, `M_Glass_Purple`, `M_RainbowGlass`, `M_StickyGlass`, `M_Crystal`, and `M_MysteryCapsule`, open the imported material and set **Blend Mode: Translucent**. Connect the imported opacity value or use a scalar around `0.2–0.5`. For best glass, use **Surface Translucency Volume** lighting mode, Metallic `0`, Roughness `0.03–0.12`, and Refraction around `1.05`.

Metal, painted shells, gold, and chrome use ordinary opaque PBR values and should import without special blend-mode edits. If Unreal reuses an older material, choose **Create New Materials** or import into a fresh folder.

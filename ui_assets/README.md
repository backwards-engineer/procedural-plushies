# Claw Game UI Art Pack

## Assets

- `splash_claw_game.png` — 1672×941 landscape splash screen.
- `button_static.png` — normal menu-button state with alpha.
- `button_hover.png` — brighter hover state with alpha.
- `button_pressed.png` — inset pressed state with alpha.
- `arrows_atlas.png` — 1774×887; left arrow occupies the left half and right arrow the right half.
- `slider_atlas.png` — track in the upper region, normal and hover knobs in the lower region.
- `progress_bars_atlas.png` — combo bar in the upper half and round-timer bar in the lower half.
- `combo_bar_empty.png` — empty combo frame and fixed star medallion.
- `combo_bar_fill.png` — isolated segmented combo fill with alpha.
- `round_timer_empty.png` — empty timer frame and fixed clock medallion.
- `round_timer_fill.png` — isolated segmented timer fill with alpha.
- `tooltip_box.png` — blank hover tooltip panel with a downward pointer.

## Unreal import

Import the splash with **Texture Group: UI** and alpha compression disabled. Import every control atlas/button with **Texture Group: UI**, **Compression Settings: UserInterface2D (RGBA)**, **sRGB enabled**, and **Mip Gen Settings: NoMipmaps** for pixel-stable menus.

The three button images intentionally contain no text; place UMG text over them so labels can be localized and reused. Give the UMG button an explicit desired size so the one-pixel source-width difference between generated states cannot cause layout movement.

Create Paper2D sprites or atlas regions for the two arrows, slider pieces, combo bar, and timer bar. Use the bar art as the frame/background and mask a duplicate fill brush horizontally for live combo/timer values.

## Animated bars

The preferred UMG structure is an `Overlay`:

1. Put the isolated fill image in a clipped track-sized container aligned to the left.
2. Drive that container's width from `MaximumTrackWidth × Percent`, or use a UI material with a scalar cutoff against UV X.
3. Draw the matching empty-frame image above the fill so the border and star/clock medallion never stretch.

Do not scale the fill texture itself along X; reveal it with clipping so the segment widths and rounded artwork stay consistent. The older combined `progress_bars_atlas.png` remains useful as a visual reference but is not needed at runtime.

Use `tooltip_box.png` as a fixed-aspect `ScaleBox` or as a nine-slice brush with conservative margins that exclude the gold corners. Place runtime title, description, rarity, and value widgets over its empty center. Position the panel above the hovered world object and let the downward pointer indicate the target.

The splash is opaque. Every other PNG—including all new empty frames, fills, and tooltip—is verified as 32-bit ARGB with genuine transparency.

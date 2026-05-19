"""
Minecraft Texture Atlas Generator
===================================
Reads all PNG block textures from a folder and packs them
into a single atlas image + JSON map file.

HOW TO USE:
1. Place this script on your Desktop (same level as mc_textures folder)
2. Run: python generate_atlas.py
3. Outputs: atlas.png and texture_map.json in the same folder
4. Upload both files to your GitHub repository
"""

import os
import json
import math
from PIL import Image

# ================================================================
#  ✏️  SETTINGS
# ================================================================

# Folder containing your extracted Minecraft block PNG textures
TEXTURE_FOLDER = "mc_textures"

# Output file names
ATLAS_OUTPUT   = "atlas.png"
MAP_OUTPUT     = "texture_map.json"

# Size of each texture tile in pixels (Minecraft uses 16x16)
TILE_SIZE = 16

# ================================================================
#  SCRIPT — No need to edit below
# ================================================================

def generate_atlas(texture_folder, atlas_output, map_output, tile_size):
    print(f"\n=== Minecraft Texture Atlas Generator ===")
    print(f"Texture folder: {texture_folder}")

    # Collect all PNG files
    if not os.path.exists(texture_folder):
        print(f"\nERROR: Folder '{texture_folder}' not found.")
        print(f"Make sure '{texture_folder}' is in the same folder as this script.")
        input("\nPress Enter to exit...")
        return

    png_files = [
        f for f in os.listdir(texture_folder)
        if f.lower().endswith('.png')
    ]

    if not png_files:
        print(f"\nERROR: No PNG files found in '{texture_folder}'.")
        input("\nPress Enter to exit...")
        return

    png_files.sort()
    total = len(png_files)
    print(f"Found {total} textures")

    # Calculate atlas grid size
    # Make it a square grid — find smallest square that fits all tiles
    cols = math.ceil(math.sqrt(total))
    rows = math.ceil(total / cols)
    atlas_w = cols * tile_size
    atlas_h = rows * tile_size

    print(f"Atlas size: {atlas_w}x{atlas_h} ({cols}x{rows} grid)")

    # Create blank atlas image (RGBA for transparency support)
    atlas = Image.new('RGBA', (atlas_w, atlas_h), (0, 0, 0, 0))

    texture_map = {}
    loaded = 0
    skipped = 0

    for index, filename in enumerate(png_files):
        filepath = os.path.join(texture_folder, filename)

        try:
            img = Image.open(filepath).convert('RGBA')

            # Only use static textures — skip animated ones
            # Animated textures are taller than wide (e.g. 16x32, 16x48)
            if img.width != tile_size:
                # Resize non-standard sizes to tile_size
                img = img.resize((tile_size, tile_size), Image.NEAREST)

            if img.height > tile_size:
                # Animated texture — crop to first frame only
                img = img.crop((0, 0, tile_size, tile_size))

            # Calculate position in atlas grid
            col = index % cols
            row = index // cols
            x = col * tile_size
            y = row * tile_size

            # Paste into atlas — use img as its own mask to preserve transparency
            # WITHOUT the mask argument, paste() ignores alpha and fills with black
            # WITH img as mask, transparent pixels stay transparent in the atlas
            atlas.paste(img, (x, y), img)

            # Record in map — use filename without extension as key
            key = os.path.splitext(filename)[0]
            texture_map[key] = {
                "u": x,
                "v": y,
                "w": tile_size,
                "h": tile_size
            }

            loaded += 1

            if loaded % 100 == 0:
                print(f"  Processed {loaded}/{total}...")

        except Exception as e:
            print(f"  Skipped {filename}: {e}")
            skipped += 1

    # Save atlas image
    atlas.save(atlas_output, 'PNG')
    atlas_size_kb = os.path.getsize(atlas_output) / 1024

    # ── Apply biome tints for grass and leaves ──
    # Vanilla Minecraft uses biome color multipliers for these textures
    # Without tinting, grass_block_top appears grey/white instead of green
    TINT_MAP = {
        'grass_block_top':          (0x79, 0xC0, 0x5A),  # Temperate grass
        'grass_block_side_overlay': (0x79, 0xC0, 0x5A),
        'oak_leaves':               (0x59, 0xAE, 0x30),  # Temperate foliage
        'dark_oak_leaves':          (0x59, 0xAE, 0x30),
        'jungle_leaves':            (0x59, 0xAE, 0x30),
        'acacia_leaves':            (0x59, 0xAE, 0x30),
        'mangrove_leaves':          (0x59, 0xAE, 0x30),
        'azalea_leaves':            (0x59, 0xAE, 0x30),
        'flowering_azalea_leaves':  (0x59, 0xAE, 0x30),
        'birch_leaves':             (0x80, 0xA7, 0x55),  # Fixed birch color
        'spruce_leaves':            (0x61, 0x99, 0x61),  # Fixed spruce color
    }

    def tint_tile(src_atlas, rect, tint_rgb):
        tile = src_atlas.crop((
            rect['u'], rect['v'],
            rect['u'] + rect['w'], rect['v'] + rect['h']
        )).convert('RGBA')
        r, g, b = tint_rgb
        pixels = tile.load()
        for ty in range(tile.height):
            for tx in range(tile.width):
                pr, pg, pb, pa = pixels[tx, ty]
                pixels[tx, ty] = ((pr*r)//255, (pg*g)//255, (pb*b)//255, pa)
        return tile

    tinted_atlas = atlas.copy()
    tinted_count = 0
    for tex_name, tint in TINT_MAP.items():
        if tex_name in texture_map:
            rect = texture_map[tex_name]
            tinted = tint_tile(atlas, rect, tint)
            tinted_atlas.paste(tinted, (rect['u'], rect['v']))
            tinted_count += 1

    tinted_output = atlas_output.replace('.png', '_tinted.png')
    tinted_atlas.save(tinted_output, 'PNG')
    tinted_size_kb = os.path.getsize(tinted_output) / 1024
    print(f"✓ Tinted atlas:  {tinted_output} ({tinted_size_kb:.0f} KB) — {tinted_count} textures tinted")

    # Save texture map JSON
    with open(map_output, 'w') as f:
        json.dump(texture_map, f, separators=(',', ':'))
    map_size_kb = os.path.getsize(map_output) / 1024

    print(f"\n✓ Atlas saved:   {atlas_output} ({atlas_size_kb:.0f} KB)")
    print(f"✓ Map saved:     {map_output} ({map_size_kb:.0f} KB)")
    print(f"✓ Textures packed: {loaded}")
    if skipped:
        print(f"  Skipped: {skipped}")
    print(f"\nNext steps:")
    print(f"  1. Upload '{atlas_output}' to your GitHub repository")
    print(f"  2. Upload '{map_output}' to your GitHub repository")
    print(f"  3. Open the viewer HTML and set BASE_URL to your GitHub Pages URL")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    texture_folder = TEXTURE_FOLDER
    atlas_output   = ATLAS_OUTPUT
    map_output     = MAP_OUTPUT

    generate_atlas(texture_folder, atlas_output, map_output, TILE_SIZE)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()

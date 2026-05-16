Workflow for Every New Build
Once (already done):

atlas.png + texture_map.json in your repo ✅

For each new build:

Export .litematic → run extract_blocks.py → get buildname.json
Upload buildname.json to GitHub
Duplicate minecraft-viewer.html → rename it
Edit only Section 1 at the top:

javascriptconst DATA_FILE    = 'buildname.json';
const TOTAL_LAYERS = 10;  // from extractor output

Upload to GitHub → embed URL in Framer


What's Configurable (marked with ✏️)

BASE_URL — your repo
DATA_FILE — your build JSON
TOTAL_LAYERS — from extractor
LAYER_MODE — cumulative or single
Camera position and target
Arrow, text, grid colors and opacity
BLOCK_TEXTURES — add any missing blocks

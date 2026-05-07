# ============================================================================
# constants.py — Centralised configuration for the Dailies Slate Generator
# ============================================================================

import os

# ------------------------------------------------------------------
# UI Options
# ------------------------------------------------------------------
DEPT_OPTIONS = ["Comp", "Roto", "Prep", "Paint", "Matchmove"]

# ------------------------------------------------------------------
# Typography and Styling
# ------------------------------------------------------------------
# Nuke reads the src/fonts directory automatically from init.py.
# Use standard family and style names rather than absolute paths.
FONT_FAMILY = "Helvetica"
FONT_STYLE_REGULAR = "Regular"
FONT_STYLE_BOLD = "Bold"

# Colors (Hex codes for Nuke: 0xRRGGBBFF)
SLATE_TEXT_COLOR = 0xCCCCCCFF  # Light grey to avoid blooming
SLATE_BG_COLOR = 0x1A1A1AFF    # Dark grey fallback if image is missing
NOTES_TEXT_COLOR = 0xE6A800FF  # Amber for visibility

# ------------------------------------------------------------------
# Nuke Nodes
# ------------------------------------------------------------------
GROUP_NODE_NAME = "submit_to_dailies"
SLATE_DURATION_FRAMES = 5

# ------------------------------------------------------------------
# Media
# ------------------------------------------------------------------
_src_dir = os.path.dirname(__file__)
SLATE_BG_IMAGE = os.path.join(_src_dir, "media", "Background.png").replace("\\", "/")

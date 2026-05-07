# ============================================================================
# Dynamic Dailies Slate Generator
# init.py — Nuke startup initialization
#
# This file is executed by Nuke on startup. It registers the plugin paths
# so Nuke can locate the tool's source code and media.
# ============================================================================

import nuke
import os

# Get the directory where this init.py file lives
_plugin_root = os.path.dirname(__file__)

# Register sub-directories with Nuke's plugin search path
nuke.pluginAddPath(os.path.join(_plugin_root, "src"))
nuke.pluginAddPath(os.path.join(_plugin_root, "src", "media"))
nuke.pluginAddPath(os.path.join(_plugin_root, "src", "fonts"))

nuke.tprint(">>> Registered Dailies Slate Generator paths")

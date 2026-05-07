# ============================================================================
# Dynamic Dailies Slate Generator
# menu.py — Entry point that starts everything
#
# Executed by Nuke after init.py (GUI mode only). Registers the toolbar
# menu, hotkey, and wires up the PySide UI.
# ============================================================================

import nuke

try:
    from src import ui_panel
    
    # Create the Nuke toolbar menu
    toolbar = nuke.menu("Nodes")
    dailies_menu = toolbar.addMenu("Dailies Tools", icon="Render.png")
    
    # Add the command and bind to a hotkey
    dailies_menu.addCommand(
        "Submit to Dailies", 
        "ui_panel.launch()", 
        "ctrl+shift+b",
        icon="Write.png"
    )
    
    nuke.tprint(">>> Loaded Dailies Slate Generator UI")
except ImportError as e:
    nuke.tprint("Failed to load Dailies Slate Generator UI: {}".format(e))

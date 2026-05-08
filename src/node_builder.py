# ============================================================================
# node_builder.py — Nuke node graph builder for dailies slate card
#
# Creates a full-frame slate info card inside a single Group node.
# Uses Background.png as the slate image, reformatted to match the
# plate resolution. The slate is shown for a specific duration then 
# switches to the plate.
# ============================================================================

import nuke
import os
from . import constants

def _create_text_node(name, message, font_size, font_family, font_style, color, box, xjustify="left", yjustify="center", global_scale=1.0):
    """
    Helper function to dynamically instantiate and configure a Nuke Text2 node.
    
    Args:
        name (str): The label identifier for the node.
        message (str): The string content to render.
        font_size (int): Base typography size.
        font_family (str): Standardized font family (e.g., 'Helvetica').
        font_style (str): Standardized font style (e.g., 'Regular').
        color (int): Hex-encoded color integer (e.g., 0xRRGGBBFF).
        box (list): The bounding box coordinates [x, y, r, t].
        xjustify (str, optional): Horizontal alignment. Defaults to "left".
        yjustify (str, optional): Vertical alignment. Defaults to "center".
        global_scale (float, optional): Multiplier for the font_size. Defaults to 1.0.
        
    Returns:
        nuke.Node: The fully configured Text2 node instance.
    """
    node = nuke.nodes.Text2(name=name)
    node["message"].setValue(message)
    node["font_size"].setValue(font_size)
    
    try:
        node["font"].setValue(font_family, font_style)
    except Exception:
        try:
            # Fallback to Times New Roman if the requested font is missing
            node["font"].setValue("Times New Roman", "Regular")
        except Exception:
            pass # Fallback to Nuke's default (Utopia)
    
    # Text2 colors are [R, G, B, A] lists, but we have a Hex int
    r = ((color >> 24) & 0xFF) / 255.0
    g = ((color >> 16) & 0xFF) / 255.0
    b = ((color >> 8) & 0xFF) / 255.0
    a = (color & 0xFF) / 255.0
    node["color"].setValue([r, g, b, a])
    
    # Box is [x, y, r, t]
    node["box"].setValue(box)
    node["xjustify"].setValue(xjustify)
    node["yjustify"].setValue(yjustify)
    node["global_font_scale"].setValue(global_scale)
    
    return node

def build_slate(data, dept, notes):
    """
    Constructs the dailies slate architecture within a single Nuke Group node.
    
    This function programmatically builds a resolution-independent node graph containing:
    1. A background canvas (Reformatted to 3840x2160 logic).
    2. A stack of Text2 nodes containing the artist, shot, and version metadata.
    3. A Switch node governed by a TCL expression to flip to the clean plate after 5 frames.
    4. A final Reformat node to conform the group's output perfectly to the script root format.
    
    Args:
        data (dict): The harvested metadata (shot, version, fps, date, etc).
        dept (str): The selected department from the UI dropdown.
        notes (str): Any multiline notes to burn into the slate.
        
    Returns:
        nuke.Node: The assembled Group node, safely connected into the DAG.
    """
    # 1. Capture selection
    selected_node = None
    try:
        nodes = nuke.selectedNodes()
        if nodes:
            # Connect to the last selected node (or the only selected node)
            selected_node = nodes[-1]
    except Exception:
        pass

    # 2. Extract values for readability
    first_frame = data.get("first_frame", 1)
    last_frame = data.get("last_frame", 100)

    # 3. Create Group Node
    group = nuke.nodes.Group(name=constants.GROUP_NODE_NAME)
    
    # Set Group tile color to a greenish color (0x4A7D4AFF)
    group['tile_color'].setValue(0x4A7D4AFF)
    
    # Add custom knobs for reference
    tab_knob = nuke.Tab_Knob("dailies_tab", "Submit Info")
    group.addKnob(tab_knob)
    
    # Populate the tab with all the fetched details as read-only labels
    group.addKnob(nuke.Text_Knob("artist", "Artist", data.get("artist", "")))
    group.addKnob(nuke.Text_Knob("shot", "Shot", data.get("shot", "")))
    group.addKnob(nuke.Text_Knob("version", "Version", data.get("version", "")))
    group.addKnob(nuke.Text_Knob("frames", "Frame Range", f"{first_frame} - {last_frame}"))
    group.addKnob(nuke.Text_Knob("fps", "FPS", str(data.get("fps", 24.0))))
    group.addKnob(nuke.Text_Knob("date", "Date", data.get("date", "")))
    group.addKnob(nuke.Text_Knob("dept", "Dept", dept))
    group.addKnob(nuke.Text_Knob("notes", "Notes", notes))

    # 4. Build internals inside the Group
    group.begin()
    
    try:
        # Input node
        input_node = nuke.nodes.Input(name="Input1")
        
        # ----------------------------------------------------
        # SLATE BACKGROUND
        # ----------------------------------------------------
        # Try to read the background image
        bg_node = None
        if os.path.exists(constants.SLATE_BG_IMAGE):
            bg_node = nuke.nodes.Read(name="Slate_Background", file=constants.SLATE_BG_IMAGE)
            
            # Reformat to match the user's 3840x2160 layout canvas
            reformat_bg = nuke.nodes.Reformat(name="Reformat_Canvas")
            reformat_bg.setInput(0, bg_node)
            reformat_bg["type"].setValue("to box")
            reformat_bg["box_width"].setValue(3840)
            reformat_bg["box_height"].setValue(2160)
            reformat_bg["box_fixed"].setValue(True)
            reformat_bg["resize"].setValue("fit")
            
            slate_base = reformat_bg
        else:
            # Fallback to constant if image is missing
            slate_base = nuke.nodes.Constant(name="Slate_Constant")
            slate_base["format"].setValue("UHD_4K")
            
            r = ((constants.SLATE_BG_COLOR >> 24) & 0xFF) / 255.0
            g = ((constants.SLATE_BG_COLOR >> 16) & 0xFF) / 255.0
            b = ((constants.SLATE_BG_COLOR >> 8) & 0xFF) / 255.0
            a = (constants.SLATE_BG_COLOR & 0xFF) / 255.0
            slate_base["color"].setValue([r, g, b, a])

        # ----------------------------------------------------
        # TEXT NODES
        # ----------------------------------------------------
        last_node = slate_base
        
        # Top-Left Stack (Info)
        info_lines = [
            ("Text_Shot", "Shot:  {}".format(data.get("shot", ""))),
            ("Text_Version", "Version:  {}".format(data.get("version", ""))),
            ("Text_Artist", "Artist:  {}".format(data.get("artist", ""))),
            ("Text_FrameRange", "Frame Range:  {} - {}".format(first_frame, last_frame)),
            ("Text_Date", "Date:  {}".format(data.get("date", ""))),
            ("Text_FPS", "FPS:  {:.1f}".format(data.get("fps", 24.0))),
        ]
        
        current_y = 2004
        for name, text in info_lines:
            txt_node = _create_text_node(
                name=name,
                message=text,
                font_size=32,
                font_family=constants.FONT_FAMILY,
                font_style=constants.FONT_STYLE_REGULAR,
                color=constants.SLATE_TEXT_COLOR,
                box=[85, current_y - 120, 1200, current_y],
                yjustify="top"
            )
            txt_node.setInput(0, last_node)
            last_node = txt_node
            current_y -= 120

        # Top-Right (Dept)
        text_dept = _create_text_node(
            name="Text_Dept",
            message=dept,
            font_size=100,
            font_family=constants.FONT_FAMILY,
            font_style=constants.FONT_STYLE_BOLD,
            color=constants.SLATE_TEXT_COLOR,
            box=[703.4, 1696.3, 3554.4, 1997.3],
            xjustify="right",
            yjustify="top",
            global_scale=3.0
        )
        text_dept.setInput(0, last_node)
        last_node = text_dept

        # Middle-Left (Notes Label)
        text_notes_label = _create_text_node(
            name="Text_NotesLabel",
            message="Submission Notes:",
            font_size=28,
            font_family=constants.FONT_FAMILY,
            font_style=constants.FONT_STYLE_BOLD,
            color=constants.NOTES_TEXT_COLOR,
            box=[85, 374, 1844, 1004],
            yjustify="top"
        )
        text_notes_label.setInput(0, last_node)
        last_node = text_notes_label
        
        # Middle-Left (Notes)
        if notes and notes.strip():
            text_notes = _create_text_node(
                name="Text_Notes",
                message=notes.strip(),
                font_size=100,
                font_family=constants.FONT_FAMILY,
                font_style=constants.FONT_STYLE_REGULAR,
                color=constants.SLATE_TEXT_COLOR,
                box=[85, 522, 3744, 874],
                yjustify="top"
            )
            text_notes.setInput(0, last_node)
            last_node = text_notes

        # Bottom-Left (Show Name - Hero)
        text_show = _create_text_node(
            name="Text_ShowName",
            message=data.get("project", ""),
            font_size=100,
            font_family=constants.FONT_FAMILY,
            font_style=constants.FONT_STYLE_BOLD,
            color=constants.SLATE_TEXT_COLOR,
            box=[85, 81.5, 2562, 282.5],
            yjustify="bottom",
            global_scale=3.0
        )
        text_show.setInput(0, last_node)
        last_node = text_show

        # ----------------------------------------------------
        # FINAL REFORMAT (Slate Format Safety)
        # ----------------------------------------------------
        # Reformat the generated 4K slate to match the root format BEFORE the switch.
        # This protects the clean plate from being reformatted or altered by the dailies node.
        final_reformat = nuke.nodes.Reformat(name="Reformat_To_Root")
        final_reformat.setInput(0, last_node)
        final_reformat["resize"].setValue("fit")
        final_reformat["black_outside"].setValue(True)

        # ----------------------------------------------------
        # SWITCH LOGIC (Slate -> Plate)
        # ----------------------------------------------------
        switch = nuke.nodes.Switch(name="Slate_Switch")
        # Input 0: Slate (Reformatted to root)
        # Input 1: Clean Plate (Untouched)
        switch.setInput(0, final_reformat)
        switch.setInput(1, input_node)
        
        # Switch expression logic:
        # frame < (first_frame + duration)
        expr = "frame < ({} + {}) ? 0 : 1".format(first_frame, constants.SLATE_DURATION_FRAMES)
        switch["which"].setExpression(expr)

        # Output node
        output_node = nuke.nodes.Output(name="Output1")
        output_node.setInput(0, switch)

    finally:
        # 5. Finish Group
        group.end()

    # 6. Auto-connect to selected node and select it
    if selected_node:
        group.setXYpos(selected_node.xpos(), selected_node.ypos() + 50)
        group.setInput(0, selected_node)
    
    # Deselect all and select the new group
    try:
        for n in nuke.allNodes():
            n.setSelected(False)
        group.setSelected(True)
    except Exception:
        pass
        
    return group

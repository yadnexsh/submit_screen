# ============================================================================
# data_extractor.py — Zero-touch data extraction
#
# Pulls artist name, shot info, frame range, resolution, and date
# automatically from the OS and the current Nuke script.
# ============================================================================

import os
import re
import getpass
import datetime

# Try to import nuke, but allow the module to be imported outside of Nuke for testing
try:
    import nuke
    _HAS_NUKE = True
except ImportError:
    _HAS_NUKE = False

def get_artist_name():
    """
    Retrieves the artist's name from the OS environment.
    
    Uses Python's built-in getpass module to securely query the active 
    OS session for the username, avoiding any hardcoded user inputs.
    
    Returns:
        str: The OS username, capitalized. Defaults to "UNKNOWN" if it fails.
    """
    try:
        return getpass.getuser()
    except Exception:
        return "UNKNOWN"

def get_script_path():
    """
    Safely retrieves the full filepath of the currently open Nuke script.
    
    Returns:
        str: The absolute path of the Nuke script. Returns empty string if Nuke
             is not active or the script hasn't been saved to disk.
    """
    if _HAS_NUKE:
        try:
            return nuke.root().name()
        except Exception:
            return ""
    return ""

def get_project_name():
    """Attempt to determine the project/show name."""
    if _HAS_NUKE:
        try:
            # Check project knob
            proj_knob = nuke.root().knob('project')
            if proj_knob and proj_knob.value():
                return proj_knob.value()
            
            # Fallback to parent directory of the script
            script_path = get_script_path()
            if script_path:
                parent_dir = os.path.basename(os.path.dirname(script_path))
                if parent_dir:
                    return parent_dir
        except Exception:
            pass
    return "Untitled Project"

def get_shot_name():
    """
    Parses the Nuke script's filepath to extract the shot name.
    
    Uses standard string splitting rules designed for the internal pipeline naming
    convention (e.g., 'ProjectName_Shot123_v001_comp.nk'). Avoids complex regex 
    for better maintainability by artists.
    
    Returns:
        str: The extracted shot name. Defaults to "UNKNOWN" if parsing fails.
    """
    script_path = get_script_path()
    if not script_path:
        return "UNKNOWN"
        
    # Get just the filename (e.g., 'SH010_comp_v01.nk')
    filename = os.path.basename(script_path)
    
    # Remove the .nk extension
    name_without_ext = filename.split('.nk')[0]
    
    # Split by underscores. We assume the first part is the shot name.
    # E.g. 'SH010_comp_v01' -> ['SH010', 'comp', 'v01'] -> 'SH010'
    parts = name_without_ext.split('_')
    
    clean_parts = []
    for part in parts:
        part_lower = part.lower()
        # Stop collecting parts if we hit a version string (e.g., 'v01')
        if part_lower.startswith('v') and part_lower[1:].isdigit():
            break
        # Stop if we hit common department names
        if part_lower in ['comp', 'roto', 'prep', 'paint', 'matchmove']:
            break
            
        clean_parts.append(part)
        
    if clean_parts:
        return "_".join(clean_parts)
        
    return name_without_ext

def get_version():
    """Extract version number (e.g. v01) from script path using simple string matching."""
    script_path = get_script_path()
    if not script_path:
        return "v00"
        
    filename = os.path.basename(script_path)
    
    # Split by underscores to find a part that looks like a version
    parts = filename.split('_')
    for part in parts:
        # Remove the .nk extension if it's on this part
        clean_part = part.split('.nk')[0]
        
        # Check if it starts with 'v' and the rest is a number
        if clean_part.lower().startswith('v') and clean_part[1:].isdigit():
            return clean_part.lower()
            
    return "v00"

def get_frame_range():
    """
    Retrieves the global sequence frame range from the Nuke script's root node.
    
    Returns:
        tuple: (first_frame, last_frame). Defaults to (1, 100) if undefined.
    """
    if _HAS_NUKE:
        try:
            # If a node is selected, try to get its frame range first
            nodes = nuke.selectedNodes()
            if nodes:
                node = nodes[0]
                if node.knob('first') and node.knob('last'):
                    return int(node.knob('first').value()), int(node.knob('last').value())
            
            # Fallback to root
            first = int(nuke.root().firstFrame())
            last = int(nuke.root().lastFrame())
            return first, last
        except Exception:
            pass
    return 1, 100

def get_fps():
    """
    Retrieves the sequence frames-per-second (FPS) setting from the script root.
    
    Returns:
        float: The active FPS. Defaults to 24.0.
    """
    if _HAS_NUKE:
        try:
            return float(nuke.root().fps())
        except Exception:
            pass
    return 24.0

def get_resolution():
    """Return the root format as (width, height) for format safety."""
    if _HAS_NUKE:
        try:
            fmt = nuke.root().format()
            return (fmt.width(), fmt.height())
        except Exception:
            pass
    return (1920, 1080)

def get_current_date():
    """
    Retrieves the current system date.
    
    Returns:
        str: Today's date formatted as YYYY-MM-DD.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_all_data():
    """Return a dictionary of all extracted data."""
    first_frame, last_frame = get_frame_range()
    width, height = get_resolution()
    
    return {
        "artist": get_artist_name(),
        "shot": get_shot_name(),
        "version": get_version(),
        "project": get_project_name(),
        "first_frame": first_frame,
        "last_frame": last_frame,
        "width": width,
        "height": height,
        "fps": get_fps(),
        "date": get_current_date()
    }

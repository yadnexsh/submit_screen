# ============================================================================
# ui_panel.py — PySide dockable panel for the Submit Info Tool
#
# Provides a clean, artist-facing UI with:
#   - Auto-populated fields (artist, shot, version, etc.)
#   - Dept dropdown
#   - Submission Notes box
#   - Generate button
# ============================================================================

import nuke
import nukescripts

# Nuke 13 and below use PySide2, Nuke 14+ uses PySide6
try:
    from PySide2.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                   QLabel, QComboBox, QTextEdit, QPushButton, 
                                   QCheckBox, QFrame, QGroupBox, QGridLayout)
    from PySide2.QtCore import Qt
except ImportError:
    from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                   QLabel, QComboBox, QTextEdit, QPushButton, 
                                   QCheckBox, QFrame, QGroupBox, QGridLayout)
    from PySide6.QtCore import Qt

from . import constants
from . import data_extractor
from . import node_builder

class SubmitToDailiesWidget(QWidget):
    def __init__(self, parent=None):
        super(SubmitToDailiesWidget, self).__init__(parent)
        self.data = {}
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Build the PySide UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # ----------------------------------------------------
        # Auto-Detected Group
        # ----------------------------------------------------
        auto_group = QGroupBox("Auto-Detected")
        auto_layout = QGridLayout()
        auto_layout.setVerticalSpacing(8)
        
        self.lbl_artist = QLabel("UNKNOWN")
        self.lbl_shot = QLabel("UNKNOWN")
        self.lbl_version = QLabel("v00")
        self.lbl_date = QLabel("YYYY-MM-DD")
        self.lbl_frames = QLabel("1 - 100")
        self.lbl_resolution = QLabel("1920 x 1080")
        self.lbl_fps = QLabel("24.0")
        self.lbl_project = QLabel("Untitled")
        
        # Make values bold
        for lbl in [self.lbl_artist, self.lbl_shot, self.lbl_version, self.lbl_date, 
                    self.lbl_frames, self.lbl_resolution, self.lbl_fps, self.lbl_project]:
            lbl.setStyleSheet("font-weight: bold;")
            
        auto_layout.addWidget(QLabel("Artist:"), 0, 0)
        auto_layout.addWidget(self.lbl_artist, 0, 1)
        
        auto_layout.addWidget(QLabel("Shot:"), 1, 0)
        auto_layout.addWidget(self.lbl_shot, 1, 1)
        
        auto_layout.addWidget(QLabel("Version:"), 2, 0)
        auto_layout.addWidget(self.lbl_version, 2, 1)
        
        auto_layout.addWidget(QLabel("Date:"), 3, 0)
        auto_layout.addWidget(self.lbl_date, 3, 1)
        
        auto_layout.addWidget(QLabel("Frames:"), 4, 0)
        auto_layout.addWidget(self.lbl_frames, 4, 1)
        
        auto_layout.addWidget(QLabel("Resolution:"), 5, 0)
        auto_layout.addWidget(self.lbl_resolution, 5, 1)
        
        auto_layout.addWidget(QLabel("FPS:"), 6, 0)
        auto_layout.addWidget(self.lbl_fps, 6, 1)
        
        auto_layout.addWidget(QLabel("Project:"), 7, 0)
        auto_layout.addWidget(self.lbl_project, 7, 1)
        
        auto_group.setLayout(auto_layout)
        main_layout.addWidget(auto_group)
        
        # ----------------------------------------------------
        # Artist Input Group
        # ----------------------------------------------------
        input_group = QGroupBox("Artist Input")
        input_layout = QVBoxLayout()
        
        # Dept Dropdown
        dept_layout = QHBoxLayout()
        dept_layout.addWidget(QLabel("Dept:"))
        self.cmb_dept = QComboBox()
        self.cmb_dept.addItems(constants.DEPT_OPTIONS)
        dept_layout.addWidget(self.cmb_dept)
        dept_layout.setStretch(1, 1)
        input_layout.addLayout(dept_layout)
        
        # Notes
        input_layout.addWidget(QLabel("Submission Notes:"))
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("e.g. Fixed edge artifacts on left side. Roto needs update.")
        self.txt_notes.setMinimumHeight(80)
        input_layout.addWidget(self.txt_notes)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # ----------------------------------------------------
        # Actions
        # ----------------------------------------------------
        # Refresh Data Button
        btn_refresh = QPushButton("Refresh Data")
        btn_refresh.clicked.connect(self.refresh_data)
        
        # Generate Button
        self.btn_generate = QPushButton("🚀 Generate Slate")
        self.btn_generate.setMinimumHeight(40)
        self.btn_generate.setStyleSheet("background-color: #4A7D4A; font-weight: bold; font-size: 14px;")
        self.btn_generate.clicked.connect(self.generate_slate)
        
        # Remove Existing Button
        self.btn_remove = QPushButton("Remove Existing Slate")
        self.btn_remove.setStyleSheet("background-color: #7D4A4A;")
        self.btn_remove.clicked.connect(self.remove_existing_slate)
        
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: #7D7D7D; font-style: italic;")
        
        main_layout.addStretch(1)
        main_layout.addWidget(btn_refresh)
        main_layout.addWidget(self.btn_generate)
        main_layout.addWidget(self.btn_remove)
        main_layout.addWidget(self.lbl_status)
        
        self.setLayout(main_layout)

    def _status(self, msg, success=True):
        """Update status label."""
        color = "#4A7D4A" if success else "#D05050"
        self.lbl_status.setStyleSheet("color: {}; font-style: italic;".format(color))
        self.lbl_status.setText(msg)

    def refresh_data(self):
        """Pull fresh data from the extractor and update UI."""
        self.data = data_extractor.get_all_data()
        
        self.lbl_artist.setText(self.data.get("artist", "UNKNOWN"))
        self.lbl_shot.setText(self.data.get("shot", "UNKNOWN"))
        self.lbl_version.setText(self.data.get("version", "v00"))
        self.lbl_date.setText(self.data.get("date", ""))
        self.lbl_frames.setText("{} - {}".format(
            self.data.get("first_frame", 1), 
            self.data.get("last_frame", 100)
        ))
        self.lbl_resolution.setText("{} x {}".format(
            self.data.get("width", 1920), 
            self.data.get("height", 1080)
        ))
        self.lbl_fps.setText(str(self.data.get("fps", 24.0)))
        self.lbl_project.setText(self.data.get("project", "Untitled"))
        
        self._status("Data refreshed.", True)

    def remove_existing_slate(self):
        """Find and delete any existing slate nodes."""
        removed = 0
        for node in nuke.allNodes("Group"):
            if node.name() == constants.GROUP_NODE_NAME:
                nuke.delete(node)
                removed += 1
        
        if removed > 0:
            self._status("Removed {} existing slate(s).".format(removed), True)
        else:
            self._status("No existing slate found to remove.", False)

    def generate_slate(self):
        """Build the Nuke node graph based on current UI data."""
        # Refresh data just in case
        self.refresh_data()
        try:
            if nuke.root().name() == "Root" or ".autosave" in nuke.root().name():
                nuke.message("Please save your Nuke script before generating a slate.\nAutosaves and unsaved scripts are not supported.")
                return

            dept = self.cmb_dept.currentText()
            notes = self.txt_notes.toPlainText()
            
            group = node_builder.build_slate(
                data=self.data, 
                dept=dept, 
                notes=notes
            )
            self._status("✅ Slate created: {}".format(group.name()), True)
        except Exception as e:
            self._status("❌ Error: {}".format(e), False)
            import traceback; traceback.print_exc()

import sys

# ------------------------------------------------------------------
# Nuke / Standalone Integration
# ------------------------------------------------------------------
window = None

def launch():
    global window

    # In Nuke, a QApplication already exists. Never create another one.
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)  # Only for standalone testing

    try:
        if window is not None:
            window.close()
    except Exception:
        pass

    window = SubmitToDailiesWidget()
    window.setWindowTitle("Submit to Dailies")
    window.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
    window.resize(450, 650)
    window.show()

if __name__ == "__main__":
    launch()

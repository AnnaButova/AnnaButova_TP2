import json
from pathlib import Path
from maya import cmds
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel
    )
from PySide6.QtGui import(
    QShortcut,
    QKeySequence
)

# ------------------------------------------------------------------------------------------
# NOTE: Undo action is mapped on Ctrl+Alt+Z due to interference with Maya's basic controls
# ------------------------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outliner Organiser")
        self.setFixedHeight(170) # define height of the window
        self.setFixedWidth(400)  # define width of the window 
        self.build_ui()

    # UNDO ----------------------------------------------------------
    def organise(self):
        cmds.undoInfo(openChunk=True, chunkName="Color Outliner Elements")
        try:
            if self.apply_colors.isChecked():
                self.attribute_color()
            if self.apply_reorder.isChecked():
                self.sort_outliner()
        finally:
            cmds.undoInfo(closeChunk=True)


    # CREATING UI ----------------------------------------------------------
    def build_ui(self):

        # Create a central widget and set layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_v = QVBoxLayout(central_widget)

        # Create a label for the file path
        self.file_path_label = QLabel("enter JSON rule path")
        layout_v.addWidget(self.file_path_label)

        # Create a line edit for the file path
        self.file_path_edit = QLineEdit()
        layout_v.addWidget(self.file_path_edit)

        # Create checkboxes
        self.apply_selection = QCheckBox("Apply on selection only")
        self.apply_colors = QCheckBox("Apply colors")
        self.apply_reorder = QCheckBox("Apply reorder")

        layout_v.addWidget(self.apply_selection)
        layout_v.addWidget(self.apply_colors)
        layout_v.addWidget(self.apply_reorder)

        # Create a button to organise
        self.organise_button = QPushButton("Organise Outliner")
        layout_v.addWidget(self.organise_button)
        self.organise_button.clicked.connect(self.organise)

        # Create Shortcut for undo 
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Alt+Z"), self)
        self.undo_shortcut.setContext(Qt.ApplicationShortcut)
        self.undo_shortcut.activated.connect(cmds.undo)


    # READ JSON FILE ----------------------------------------------------------
    def read_json_file(self): # reads JSON file
        file_path = self.file_path_edit.text() # converts user input to str
        if Path(file_path).is_file(): # checks if the file exists
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    print("JSON data loaded successfully:")
                    return(data) # returns data from json
                except json.JSONDecodeError as e: # in case of error, prints error message
                    print(f"Error decoding JSON: {e}")
        else:
            print("File does not exist.")


    # APPLY COLOR TO OUTLINER OBJECTS ----------------------------------------------------------
    def attribute_color(self):
        json_data = self.read_json_file() # gets info from json file

        if self.apply_colors.isChecked() and self.apply_selection.isChecked(): # applies colors to selected objects only
            for i in cmds.ls(selection=True):
                    for key, value in json_data.items():
                        if i.startswith(key): # if object name starts with one of json's keys (such as SM_, LGT_ or FX_ in this case)
                            cmds.setAttr(f"{i}.useOutlinerColor", 1) # tells Maya to show the color in outline
                            cmds.setAttr(f"{i}.outlinerColor", value[0], value[1], value[2], type = "float3") # applies color to object based on json's values
        elif self.apply_colors.isChecked(): # applies colors to ALL objects
                    for i in cmds.ls():
                            for key, value in json_data.items(): 
                                if i.startswith(key): # if object name starts with one of json's keys (such as SM_, LGT_ or FX_ in this case)
                                    cmds.setAttr(f"{i}.useOutlinerColor", 1) # tells Maya to show the color in outline
                                    cmds.setAttr(f"{i}.outlinerColor", value[0], value[1], value[2], type = "float3") # applies color to object based on json's values
        

    # SORTING OUTLINER ----------------------------------------------------------
    def sort_outliner(self):
        json_data = self.read_json_file() # gets info from json file
        sorted_data = dict(sorted(json_data.items()))  # sorts info in json (alphabetically)

        if self.apply_reorder.isChecked() and self.apply_selection.isChecked: # sorts selected objects
            for key in sorted_data.keys():
                object_list = [] # making a list to store objects in "categories" (according to keys)
                for i in cmds.ls(selection=True, type="transform"): # all objects in outliner
                    if i.startswith(key): 
                        object_list.append(i) # adds object to the list
                sorted_outliner = sorted(object_list, key=lambda name: int(name.split("_")[1])) # splits object (prefix - number - suffix), then sorts according to number
                for object in sorted_outliner: 
                    cmds.reorder(object, back=True) # reorders the objects in MAYA outliner
        elif self.apply_reorder.isChecked(): # sorts ALL objects
                    for key in sorted_data.keys():
                        object_list = [] # making a list to store objects in "categories" (according to keys)
                        for i in cmds.ls(type="transform"): # all objects in outliner
                            if i.startswith(key):
                                object_list.append(i) # adds object to the list
                        sorted_outliner = sorted(object_list, key=lambda name: int(name.split("_")[1])) # splits object (prefix - number - suffix), then sorts according to number
                        for object in sorted_outliner: 
                            cmds.reorder(object, back=True) # reorders the objects in MAYA outliner

window = MainWindow()
window.show()

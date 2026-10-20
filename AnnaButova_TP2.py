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
            self.attribute_color()
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
        json_data = self.read_json_file()

        if self.apply_colors.isChecked():
            for i in cmds.ls():
                    for key, value in json_data.items():
                        if i.startswith(key):
                            cmds.setAttr(f"{i}.useOutlinerColor", 1)
                            cmds.setAttr(f"{i}.outlinerColor", value[0], value[1], value[2], type = "float3")

    # SORTING OUTLINER ----------------------------------------------------------
    def sort_outliner(self):
        json_data = self.read_json_file()
        sorted_data = dict(sorted(json_data.items()))
        #print(sorted_data)

        if self.apply_reorder.isChecked():
            for key in sorted_data.keys():
                object_list = []
                for i in cmds.ls(type="transform"):
                    if i.startswith(key):
                        object_list.append(i)
                sorted_outliner = sorted(object_list, key=lambda name: int(name.split("_")[1]))
                print(sorted_outliner)
                for object in sorted_outliner:
                    cmds.reorder(object, back=True)

       
        
                        



window = MainWindow()
window.show()

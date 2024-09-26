import sys
import os

from pymxs import runtime as rt
import qtmax
from PySide2 import QtCore, QtWidgets
from pxr import Usd, UsdShade

if os.path.dirname(os.path.dirname(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import MaterialImporter


class MaterialListWindow(QtWidgets.QDialog):
    def __init__(self, usd_file):
        super(MaterialListWindow, self).__init__(qtmax.GetQMaxMainWindow())

        stage = Usd.Stage.Open(usd_file)
        self.material_importer = MaterialImporter.MaterialImporter(stage)

        self.setWindowTitle("USD Material Importer " + usd_file)

        v_material_layout = QtWidgets.QVBoxLayout()
        v_material_layout.addWidget(QtWidgets.QLabel('Materials', self))
        self.list_materials = QtWidgets.QListWidget(self)
        v_material_layout.addWidget(self.list_materials)
        self.list_materials.currentItemChanged.connect(self.list_materials_seletionChanged)

        v_shader_layout = QtWidgets.QVBoxLayout()
        v_shader_layout.addWidget(QtWidgets.QLabel('Shaders', self))
        self.list_shaders = QtWidgets.QListWidget(self)
        v_shader_layout.addWidget(self.list_shaders)

        self.import_button = QtWidgets.QPushButton('Import', self)
        self.import_button.clicked.connect(self.button_import_clicked)

        v_layout = QtWidgets.QVBoxLayout()
        h_layout = QtWidgets.QHBoxLayout()
        v_layout.addLayout(h_layout)
        h_layout.addLayout(v_material_layout)
        h_layout.addLayout(v_shader_layout)
        v_layout.addWidget(self.import_button)
        self.setLayout(v_layout)

        self.init_list_materials()

    def init_list_materials(self):
        material_prims = []
        for prim in self.material_importer.stage.Traverse():
            if prim.IsA(UsdShade.Material):
                material_prims.append(prim)

        for material in material_prims:
            self.list_materials.addItem(str(material.GetPath()))

        if len(material_prims) > 0:
            self.list_materials.setCurrentRow(0)

    def list_materials_seletionChanged(self):
        self.list_shaders.clear()

        selected_material = self.list_materials.currentItem().text()
        material_prim = self.material_importer.stage.GetPrimAtPath(
            selected_material)

        shader_prims = []
        for material_attr in material_prim.GetAttributes():
            for material_connection in material_attr.GetConnections():
                child_prim = self.material_importer.stage.GetPrimAtPath(material_connection.GetPrimPath())
                if child_prim.IsA(UsdShade.Shader):
                    shader_prims.append(child_prim)
                elif child_prim.IsA(UsdShade.NodeGraph):
                    for child_attr in child_prim.GetAttributes():
                        for child_connection in child_attr.GetConnections():
                            shader_prim = self.material_importer.stage.GetPrimAtPath(child_connection.GetPrimPath())
                            if shader_prim.IsA(UsdShade.Shader):
                                shader_prims.append(shader_prim)

        for shader_prim in shader_prims:
            id = shader_prim.GetAttribute('info:id').Get()
            item = QtWidgets.QListWidgetItem(id)
            item.setData(QtCore.Qt.UserRole,
                         shader_prim.GetPrimPath().pathString)
            self.list_shaders.addItem(item)

        if len(shader_prims) > 0:
            self.list_shaders.setCurrentRow(0)

    def button_import_clicked(self):
        item = self.list_shaders.currentItem()
        if item is None:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Please select a shader.')
            return

        selected_nodes = rt.selection
        if len(selected_nodes) == 0:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Please select a node.')
            return

        shader_path = item.data(QtCore.Qt.UserRole)
        material = self.material_importer.create_material_node(shader_path)

        for node in selected_nodes:
            node.material = material

        rt.redrawViews()


def main():
    usd_file = QtWidgets.QFileDialog.getOpenFileName(None, 'Open USD File', '', 'USD File (*.usd *.usda *.usdc *.usdz)')[0]
    if not usd_file:
        return

    dialog = MaterialListWindow(usd_file)
    dialog.show()

    return dialog


dialog = main()

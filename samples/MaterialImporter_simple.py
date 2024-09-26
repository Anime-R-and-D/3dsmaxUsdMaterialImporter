import sys
import os
import importlib

from pxr import Usd
from pymxs import runtime as rt

if os.path.dirname(os.path.dirname(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import MaterialImporter
importlib.reload(MaterialImporter)

USD_FILE_PATH = "WRITE YOUR USD FILE PATH"
MATERIAL_SDF_PATH = "WRITE YOUR MATERIAL SDF PATH IN USD FILE"

def main() -> None:
    stage = Usd.Stage.Open(USD_FILE_PATH)
    stage.Reload()

    material_importer = MaterialImporter.MaterialImporter(stage)

    sphere = rt.sphere()
    sphere.mapcoords = True
    sphere.material = material_importer.create_material_node(MATERIAL_SDF_PATH)


main()

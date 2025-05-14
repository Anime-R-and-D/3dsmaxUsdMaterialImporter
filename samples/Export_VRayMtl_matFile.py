import sys
import os

from pymxs import runtime as rt
from pxr import Usd, UsdShade, Sdf

if os.path.dirname(os.path.dirname(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import MaterialImporter


def collect_VRayMtl_paths(stage: Usd.Stage) -> list[Sdf.Path]:
    dst: list[Sdf.Path] = []

    for prim in stage.Traverse():
        if prim.IsA(UsdShade.Material) == False:
            continue

        outputs = UsdShade.Material(prim).GetSurfaceOutputs()
        for output in outputs:
            if output.GetBaseName() != "vray:surface":
                continue

            vray_prim = output.GetConnectedSource()[0]
            shader_path = vray_prim.GetOutput("surface").GetConnectedSource()[0].GetPath()
            dst.append(shader_path)

    return dst


def export_VRayMtl_matFile(usd_file: str, mat_file: str):
    stage = Usd.Stage.Open(usd_file)
    material_importer = MaterialImporter.MaterialImporter(stage)

    material_library = rt.MaterialLibrary()

    for shader_path in collect_VRayMtl_paths(stage):
        print(shader_path)
        vray_mtl = material_importer.create_material_node(shader_path)
        rt.append(material_library, vray_mtl)

    rt.saveTempMaterialLibrary(material_library, mat_file)


def main():
    usd_file: str = rt.getOpenFileName(caption="Open USD File", types="USD Files (*.usd *.usda *.usdc)|*.usd;*.usda;*.usdc|All Files (*.*)|*.*")
    if not usd_file:
        return

    mat_file: str = rt.getSaveFileName(caption="Save Material File", types="Material Files (*.mat)|*.mat|All Files (*.*)|*.*")
    if not mat_file:
        return

    export_VRayMtl_matFile(usd_file, mat_file)


if __name__ == "__main__":
    main()

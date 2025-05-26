import sys
import os
from typing import Any, Optional

from pymxs import runtime as rt
from pxr import Usd, UsdGeom, UsdShade

if os.path.dirname(os.path.dirname(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import MaterialImporter
from samples import Export_VRayMtl_matFile


def get_max_node_by_path(path: str) -> Optional[rt.Node]:
    paths = path.split("/")

    root_nodes: dict[str, rt.Node] = {o.name: o for o in rt.objects if o.parent is None}
    if paths[0] not in root_nodes:
        return None

    node = root_nodes[paths[0]]
    for name in paths[1:]:
        for child in node.children:
            if child.name == name:
                node = child
                break
        else:
            return None

    return node


class MaterialReplacer:
    shader_names = ["vray:surface"]

    def __init__(self, stage: Usd.Stage):
        self.stage = stage
        self.max_mtls: dict[str, Any] = self.import_max_mtls_from_stage()

    def import_max_mtls_from_stage(self) -> Any:
        raise NotImplementedError

    def get_usd_bound_shader_path(self, mesh: UsdGeom.Mesh) -> UsdShade.Material | None:
        binding_api = UsdShade.MaterialBindingAPI(mesh)
        materials = binding_api.ComputeBoundMaterial()

        if len(materials) == 0:
            return None

        material: UsdShade.Material = materials[0]
        if material.GetPrim().IsValid() == False:
            return None

        output_dict = {o.GetBaseName(): o.GetConnectedSource()[0] for o in material.GetSurfaceOutputs() if o.GetConnectedSource()}
        output_list = [output_dict[shader_name] for shader_name in self.shader_names if shader_name in output_dict]
        if len(output_list) == 0:
            return None

        material_output = output_list[0]
        if material_output.GetPrim().IsA(UsdShade.Shader):
            return material_output.GetPath()
        elif material_output.GetPrim().IsA(UsdShade.NodeGraph):
            shader_prim = material_output.GetOutput("surface").GetConnectedSource()[0]
            if shader_prim.GetPrim().IsA(UsdShade.Shader) == False:
                raise Exception(f"NotShaderPrimError: {shader_prim.GetPath()}")
            return shader_prim.GetPath()
        else:
            raise Exception("MaterialOutputTypeError: " + str(material_output))

    def set_mesh_material(self, mesh: UsdGeom.Mesh, node: rt.Node) -> None:
        usd_bound_shader_path = self.get_usd_bound_shader_path(mesh)
        if usd_bound_shader_path is not None and str(usd_bound_shader_path) in self.max_mtls:
            node.material = self.max_mtls[str(usd_bound_shader_path)]

    def replace_submtls(self, multi_mat: Any, subsets: list[UsdGeom.Subset]) -> None:
        subset_names = {subset.GetPath().name: subset for subset in subsets}

        for i in range(multi_mat.numsubs):
            sub_name = multi_mat.names[i]
            if sub_name not in subset_names:
                continue
            subset = subset_names[sub_name]
            usd_bound_shader_path = self.get_usd_bound_shader_path(subset)
            if usd_bound_shader_path is not None and str(usd_bound_shader_path) in self.max_mtls:
                multi_mat[i] = self.max_mtls[str(usd_bound_shader_path)]

    def assign_mtls(self) -> None:
        for prim in self.stage.Traverse():
            if prim.IsA(UsdGeom.Mesh) == False:
                continue

            mesh = UsdGeom.Mesh(prim)

            max_path = str(mesh.GetPath())[1:]
            max_node = get_max_node_by_path(max_path)
            if max_node is None:
                print("max node not found:", max_path)
                return

            geom_subsets = UsdGeom.Subset.GetAllGeomSubsets(mesh)
            if len(geom_subsets) == 0:
                self.set_mesh_material(mesh, max_node)
            else:
                max_mtl = max_node.material
                if rt.isKindOf(max_mtl, rt.Multimaterial):
                    self.replace_submtls(max_mtl, geom_subsets)
                    if max_mtl.numsubs == 1:
                        max_node.material = max_mtl[0]
                else:
                    self.set_mesh_material(mesh, max_node)


class MaterialReplacer_VRayMtl(MaterialReplacer):
    def import_max_mtls_from_stage(self) -> dict[str, Any]:
        importer = MaterialImporter.MaterialImporter(self.stage)
        vray_mtls = {str(path): importer.create_material_node(path) for path in Export_VRayMtl_matFile.collect_VRayMtl_paths(self.stage)}
        print(len(vray_mtls), "VRayMtls are created.")
        return vray_mtls


def assing_VrayMtls(usd_file: str) -> None:
    stage = Usd.Stage.Open(usd_file)
    stage.Reload()
    MaterialReplacer_VRayMtl(stage).assign_mtls()


def deduplicate_MultiMaterials():
    def generate_id(multi_mat: Any) -> str:
        addrs = [rt.refs.getAddr(multi_mat[i]) for i in range(multi_mat.numsubs)]
        return str(addrs)

    multi_mats = {generate_id(m): m for m in rt.sceneMaterials if rt.isKindOf(m, rt.Multimaterial)}

    for obj in rt.objects:
        old_mtl = obj.material
        if rt.isKindOf(old_mtl, rt.Multimaterial):
            id = generate_id(old_mtl)
            obj.material = multi_mats[id]


def main() -> None:
    usd_file = rt.getOpenFileName(caption="Open USD file", types="USD (*.usd; *.usda; *.usdc)|*.usd; *.usda; *.usdc|All Files (*)|*")
    if not usd_file:
        return

    rt.USDImporter.importFile(usd_file)
    assing_VrayMtls(usd_file)
    deduplicate_MultiMaterials()


if __name__ == "__main__":
    main()

import importlib.util
import pathlib
import traceback
import types
from typing import Union, Callable, Any

from pymxs import runtime as rt
from pxr import Usd


class MaterialImporter:
    def __init__(self, stage: Usd.Stage) -> None:
        self.stage = stage
        self.materials: dict[str, rt.Material] = {}

        self.material_modules: dict[pathlib.Path, dict[str, str | Any]] = {}

        for __init__py in pathlib.Path(__file__).parent.glob("**/__init__.py"):
            module_dir = __init__py.parent
            self.material_modules[module_dir] = {}
            spec = importlib.util.spec_from_file_location(__init__py.as_posix(), __init__py)  # type: ignore
            module = importlib.util.module_from_spec(spec)  # type: ignore
            spec.loader.exec_module(module)  # type: ignore
            self.material_modules[module_dir] = module.get_generaters()

    def get_id_module(self, id: str) -> Any | None:
        for dir_path, id_modules in self.material_modules.items():
            if id in id_modules:
                if isinstance(id_modules[id], str):
                    py_file = dir_path / id_modules[id]
                    spec = importlib.util.spec_from_file_location(py_file.as_posix(), py_file)
                    module = importlib.util.module_from_spec(spec)  # type: ignore
                    spec.loader.exec_module(module)  # type: ignore
                    id_modules[id] = module
                return id_modules[id]

        return None

    def set_attrs(self, mat: rt.Material, prim: Usd.Prim, input_mat_prop_names: dict[str, Callable[[dict[str, Any]], None] | str | None]) -> None:
        for usd_attr in prim.GetAttributes():
            usd_attr_name: str = usd_attr.GetName()
            if usd_attr_name.startswith("inputs:") == False:
                continue

            connections = usd_attr.GetConnections()
            usd_value = usd_attr.Get()
            values = {"material_node": mat, "usd_value": None, "stage": self.stage, "material_importer": self}

            mat_attr = input_mat_prop_names.get(usd_attr_name[7:], None)
            if mat_attr is None:
                continue
            elif isinstance(mat_attr, str):
                if len(connections) > 0:
                    for connection in connections:
                        child_mat = self.create_material_node(connection.GetPrimPath())
                        setattr(mat, mat_attr, child_mat)
                else:
                    setattr(mat, mat_attr, usd_value)
            elif isinstance(mat_attr, types.FunctionType):
                if len(connections) > 0:
                    for connection in connections:
                        values["usd_value"] = connection
                        mat_attr(values)
                else:
                    values["usd_value"] = usd_value
                    mat_attr(values)
            else:
                raise NotImplementedError

    def create_material_node(self, sdf_path: str) -> Union[rt.Material, None]:
        if sdf_path in self.materials:
            return self.materials[sdf_path]

        try:
            shader = self.stage.GetPrimAtPath(sdf_path)
            id: str = shader.GetAttribute('info:id').Get()

            module = self.get_id_module(id)
            if module is None:
                return None

            scene_name = shader.GetAttribute('inputs:scene_name').Get()
            node_name: str = scene_name[0] if scene_name else shader.GetName()

            mat = module.genarate_material_node_from_usd_prim(shader, self)
            mat.name = node_name

            self.materials[sdf_path] = mat

            return mat
        except:
            traceback.print_exc()
            return None

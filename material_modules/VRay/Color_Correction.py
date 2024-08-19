from typing import Any, Callable

from pxr import Usd
from pymxs import runtime as rt

def genarate_material_node_from_usd_prim(usd_shader: Usd.Prim, material_importer: Any) -> rt.Material:
    node = rt.Color_Correction()

    for texture_output_path in usd_shader.GetAttribute("inputs:texture_map").GetConnections():
        node.map = material_importer.create_material_node(texture_output_path.GetPrimPath())

    node.saturation = usd_shader.GetAttribute("inputs:saturation").Get() * 100

    return node

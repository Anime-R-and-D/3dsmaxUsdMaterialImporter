from typing import Any, Callable

from pxr import Usd
from pymxs import runtime as rt

def genarate_material_node_from_usd_prim(usd_shader: Usd.Prim, material_importer: Any) -> rt.Material:
    node = rt.VRayNormalMap()

    vray_TexBitmap_path = usd_shader.GetAttribute("inputs:bump_tex_color").GetConnections()[0].GetPrimPath()
    node.normal_map = material_importer.create_material_node(vray_TexBitmap_path)

    return node

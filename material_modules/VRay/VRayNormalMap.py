from typing import Any

from pxr import Usd
from pymxs import runtime as rt


def genarate_material_node_from_usd_prim(usd_shader: Usd.Prim, material_importer: Any) -> rt.Material:
    node = rt.VRayNormalMap()

    vray_TexBitmap_path = usd_shader.GetAttribute("inputs:bump_tex_color").GetConnections()[0].GetPrimPath()

    bump_tex_color_prim = usd_shader.GetStage().GetPrimAtPath(vray_TexBitmap_path)
    if bump_tex_color_prim.GetAttribute('info:id').Get() == "vray:TexNormalMapFlip":
        for attr_name in ["flip_red", "flip_green", "swap_red_and_green"]:
            setattr(node, attr_name, bump_tex_color_prim.GetAttribute(f"inputs:{attr_name}").Get())
        vray_TexBitmap_path = bump_tex_color_prim.GetAttribute("inputs:texmap").GetConnections()[0].GetPrimPath()

    node.normal_map = material_importer.create_material_node(vray_TexBitmap_path)

    return node

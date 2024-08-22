from typing import Any

from pxr import Usd
from pymxs import runtime as rt


def genarate_material_node_from_usd_prim(usd_shader: Usd.Prim, material_importer: Any) -> rt.Material:
    node = rt.Mix()

    for input_attr, dst_attr in [("color1", "map1"), ("color2", "map2")]:
        for texture_output_path in usd_shader.GetAttribute(f"inputs:{input_attr}").GetConnections():
            texture = material_importer.create_material_node(texture_output_path.GetPrimPath())
            setattr(node, dst_attr, texture)

    for vray_TexFloatToColor_prim_output in usd_shader.GetAttribute(f"inputs:mix_map").GetConnections():
        vray_TexFloatToColor_prim = material_importer.stage.GetPrimAtPath(vray_TexFloatToColor_prim_output.GetPrimPath())
        texture_output_path = vray_TexFloatToColor_prim.GetAttribute("inputs:input").GetConnections()[0]
        texture = material_importer.create_material_node(texture_output_path.GetPrimPath())
        node.Mask = texture

    node.mixAmount = usd_shader.GetAttribute("inputs:mix_amount").Get() * 100

    return node

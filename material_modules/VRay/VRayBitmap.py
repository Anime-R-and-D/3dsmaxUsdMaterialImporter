from typing import Any, Callable

from pxr import Usd
from pymxs import runtime as rt

def genarate_material_node_from_usd_prim(usd_shader: Usd.Prim, material_importer: Any) -> rt.Material:
    node = rt.VRayBitmap()

    node.Output.alphaFromRGB = usd_shader.GetAttribute("inputs:alpha_from_intensity").Get()

    bitmap_buffer_path = usd_shader.GetAttribute("inputs:bitmap").GetConnections()[0].GetPrimPath()
    bitmap_buffer_prim = material_importer.stage.GetPrimAtPath(bitmap_buffer_path)

    bitmap_path = bitmap_buffer_prim.GetAttribute("inputs:file").Get()
    node.HDRIMapName = bitmap_path.path
    node.color_space = bitmap_buffer_prim.GetAttribute("inputs:color_space").Get()

    return node

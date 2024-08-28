from typing import Any

def get_generaters() -> dict[str, str | Any]:
    return {
        "vray:ColorCorrection": "Color_Correction.py",
        "vray:TexMix": "Mix.py",
        "vray:TexBitmap": "VRayBitmap.py",
        "vray:MtlSingleBRDF": "VRayMtl.py",
        "vray:TexNormalBump": "VRayNormalMap.py",
    }

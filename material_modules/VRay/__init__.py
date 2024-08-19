from typing import Any

def get_generaters() -> dict[str, str | Any]:
    return {
        "vray:MtlSingleBRDF": "VRayMtl.py",
        "vray:TexBitmap": "VRayBitmap.py",
        "vray:ColorCorrection": "Color_Correction.py",
    }

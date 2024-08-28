from typing import Any, Callable

from pxr import Usd, Gf, Sdf
from pymxs import runtime as rt


def __set_vray_map(values: dict[str, Any], attr_type_name: str) -> None:
    material_node = values["material_node"]
    usd_value = values["usd_value"]
    stage = values["stage"]
    material_importer = values["material_importer"]

    color_attr_name = attr_type_name[0].upper() + attr_type_name[1:]

    if isinstance(usd_value, Gf.Vec3f):
        setattr(material_node, color_attr_name, rt.Point3(*(usd_value * 255)))
    elif isinstance(usd_value, Sdf.Path):
        prim = stage.GetPrimAtPath(usd_value.GetPrimPath())
        id = prim.GetAttribute('info:id').Get()

        if id == "vray:TexCombineColor":
            texture_output_paths = prim.GetAttribute("inputs:texture").GetConnections()

            color = prim.GetAttribute("inputs:color").Get()
            setattr(material_node, color_attr_name, rt.Point3(*(color * 255)))
        elif id == "vray:TexAColorOp":
            texture_output_paths = prim.GetAttribute("inputs:color_a").GetConnections()
        else:
            texture_output_paths = [prim.GetPath()]

        for texture_output_path in texture_output_paths:
            texture_node = material_importer.create_material_node(texture_output_path.GetPrimPath())
            setattr(material_node, f"texmap_{attr_type_name}", texture_node)
    else:
        raise NotImplementedError


def set_vray_map(attr_type_name: str) -> Callable[[dict[str, Any]], None]:
    return lambda values: __set_vray_map(values, attr_type_name)


def genarate_material_node_from_usd_prim(usd_shader: Usd.Prim, material_importer: Any) -> rt.Material:
    mat = rt.VRayMtl()
    usd_stage = usd_shader.GetStage()
    brdfs = usd_shader.GetAttribute("inputs:brdf").GetConnections()

    for brdf in brdfs:
        brdf_prim = usd_stage.GetPrimAtPath(brdf.GetPrimPath())
        material_importer.set_attrs(mat, brdf_prim, input_mat_prop_names)

    return mat


input_mat_prop_names: dict[str, Callable[[dict[str, Any]], None] | str | None] = {
    "anisotropy": None,
    "anisotropy_axis": None,
    "anisotropy_derivation": None,
    "anisotropy_rotation": None,
    "brdf_type": None,
    "bump_map": set_vray_map("bump"),
    "coat_amount": None,
    "coat_bump_lock": None,
    "coat_color": None,
    "coat_glossiness": None,
    "coat_ior": None,
    "compensate_camera_exposure": None,
    "diffuse": set_vray_map("diffuse"),
    "dispersion": None,
    "dispersion_on": None,
    "environment_priority": None,
    "fog_bias": None,
    "fog_color": lambda values: setattr(values["material_node"], "refraction_fogColor", rt.Point3(*(values["usd_value"] * 255))),
    "fog_depth": None,
    "fog_mult": None,
    "fog_unit_scale_on": None,
    "fresnel": None,
    "fresnel_ior": None,
    "fresnel_ior_lock": None,
    "gtr_energy_compensation": None,
    "gtr_gamma": None,
    "hilight_glossiness_lock": None,
    "hilight_soften": None,
    "lpe_label": None,
    "metalness": None,
    "new_gtr_anisotropy": None,
    "opacity": None,
    "opacity_color": set_vray_map("opacity"),
    "opacity_mode": None,
    "option_cutoff": None,
    "option_double_sided": None,
    "option_energy_mode": None,
    "option_fix_dark_edges": None,
    "option_glossy_rays_as_gi": None,
    "option_reflect_on_back": None,
    "option_use_irradiance_map": None,
    "option_use_roughness": None,
    "reflect": set_vray_map("reflection"),
    "reflect_affect_alpha": None,
    "reflect_depth": None,
    "reflect_dim_distance": None,
    "reflect_dim_distance_falloff": None,
    "reflect_dim_distance_on": None,
    "reflect_exit_color": None,
    "reflect_glossiness": set_vray_map("reflectionGlossiness"),
    "reflect_subdivs": None,
    "reflect_trace": None,
    "refract": set_vray_map("refraction"),
    "refract_affect_alpha": None,
    "refract_affect_shadows": None,
    "refract_depth": None,
    "refract_exit_color": None,
    "refract_exit_color_on": None,
    "refract_glossiness": None,
    "refract_ior": None,
    "refract_subdivs": None,
    "refract_thin_walled": None,
    "refract_trace": None,
    "roughness": None,
    "roughness_model": None,
    "self_illumination": None,
    "self_illumination_gi": None,
    "sheen_color": None,
    "sheen_glossiness": None,
    "thin_film_ior": None,
    "thin_film_on": None,
    "thin_film_thickness": None,
    "thin_film_thickness_max": None,
    "thin_film_thickness_min": None,
    "translucency": None,
    "translucency_amount": None,
    "translucency_color": None,
    "translucency_light_mult": None,
    "translucency_scatter_coeff": None,
    "translucency_scatter_dir": None,
    "translucency_surfaceLighting": None,
    "translucency_thickness": None,
    "use_environment_override": None,
}

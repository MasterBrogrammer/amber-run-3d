"""Build Amber Run 3D sprites inside the live Blender session."""
from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path("/Users/stevenwoolery/amber-run-3d")
OUT_PLAYER = ROOT / "assets" / "player"
OUT_WORLD = ROOT / "assets" / "world"
BLEND = ROOT / "blender" / "amber_assets.blend"

OUT_PLAYER.mkdir(parents=True, exist_ok=True)
OUT_WORLD.mkdir(parents=True, exist_ok=True)


def _clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.lights,
        bpy.data.cameras,
        bpy.data.curves,
        bpy.data.worlds,
        bpy.data.images,
        bpy.data.actions,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def _collection(name: str) -> bpy.types.Collection:
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def _link(obj: bpy.types.Object, coll_name: str) -> bpy.types.Object:
    dest = _collection(coll_name)
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    dest.objects.link(obj)
    return obj


def _set_in(node, names, value) -> None:
    for name in names:
        if name in node.inputs:
            node.inputs[name].default_value = value
            return


def make_mat(
    name: str,
    color,
    roughness: float = 0.42,
    metallic: float = 0.0,
    emission=None,
    emission_strength: float = 0.0,
    specular: float = 0.5,
) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    principled = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    _set_in(principled, ["Base Color"], (*color, 1.0))
    _set_in(principled, ["Roughness"], roughness)
    _set_in(principled, ["Metallic"], metallic)
    _set_in(principled, ["Specular IOR Level", "Specular"], specular)
    if emission is not None:
        _set_in(principled, ["Emission Color", "Emission"], (*emission, 1.0))
        _set_in(principled, ["Emission Strength"], emission_strength)
    return mat


def assign(obj: bpy.types.Object, mat_name: str) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(bpy.data.materials[mat_name])


def add_mesh(op: str, name: str, coll: str, **kwargs) -> bpy.types.Object:
    getattr(bpy.ops.mesh, op)(**kwargs)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    _link(obj, coll)
    return obj


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def hide_all_except(keep: set[str]) -> None:
    for obj in bpy.data.objects:
        hide = True
        for col in obj.users_collection:
            if col.name in keep:
                hide = False
        if obj.type in {"CAMERA", "LIGHT"}:
            hide = False
        obj.hide_render = hide
        obj.hide_viewport = hide and obj.type not in {"CAMERA", "LIGHT"}


def setup_scene() -> None:
    _clear_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.fps = 12
    scene.frame_start = 1
    scene.frame_end = 8
    eevee = scene.eevee
    eevee.taa_render_samples = 32
    if hasattr(eevee, "use_raytracing"):
        eevee.use_raytracing = True
    if hasattr(eevee, "use_shadows"):
        eevee.use_shadows = True
    if hasattr(eevee, "use_fast_gi"):
        eevee.use_fast_gi = True

    world = bpy.data.worlds.new("AmberWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.04, 0.03, 0.07, 1.0)
    bg.inputs[1].default_value = 0.15

    make_mat("Coral", (0.96, 0.42, 0.32), roughness=0.38)
    make_mat("Belly", (1.0, 0.72, 0.38), roughness=0.4)
    make_mat("Eye", (0.08, 0.06, 0.1), roughness=0.25)
    make_mat("Shine", (1.0, 0.97, 0.92), roughness=0.12, emission=(1.0, 0.97, 0.92), emission_strength=0.8)
    make_mat("Stone", (0.18, 0.14, 0.24), roughness=0.62)
    make_mat("AmberRim", (0.96, 0.55, 0.28), roughness=0.28, emission=(0.96, 0.5, 0.2), emission_strength=0.35)
    make_mat("Gold", (1.0, 0.78, 0.22), roughness=0.18, metallic=0.85)
    make_mat("Pole", (0.82, 0.78, 0.7), roughness=0.35, metallic=0.35)
    make_mat("Banner", (0.92, 0.28, 0.24), roughness=0.48)
    make_mat("Ground", (0.12, 0.09, 0.16), roughness=0.7)
    make_mat("GroundRim", (0.34, 0.17, 0.2), roughness=0.5)
    make_mat("Hill", (0.1, 0.07, 0.14), roughness=0.8)
    make_mat("Sun", (1.0, 0.84, 0.42), roughness=0.35, emission=(1.0, 0.82, 0.4), emission_strength=22.0)

    cam_data = bpy.data.cameras.new("SpriteCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.1
    cam_data.clip_start = 0.05
    cam_data.clip_end = 80.0
    cam = bpy.data.objects.new("SpriteCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (1.15, -6.4, 1.28)
    look_at(cam, Vector((0.0, 0.0, 0.55)))
    scene.camera = cam

    def add_light(name, ltype, loc, energy, color, rot=None, size=2.4):
        data = bpy.data.lights.new(name=name, type=ltype)
        data.energy = energy
        data.color = color
        if ltype == "AREA":
            data.size = size
        if ltype == "SUN":
            data.angle = math.radians(12)
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        if rot:
            obj.rotation_euler = rot
        bpy.context.scene.collection.objects.link(obj)
        return obj

    key = add_light("Key", "AREA", (3.4, -3.2, 4.6), 280, (1.0, 0.72, 0.42), size=3.2)
    look_at(key, Vector((0, 0, 0.5)))
    fill = add_light("Fill", "AREA", (-3.6, -2.4, 2.4), 70, (0.45, 0.32, 0.7), size=4.0)
    look_at(fill, Vector((0, 0, 0.5)))
    rim = add_light("Rim", "AREA", (-1.2, 3.8, 3.2), 110, (1.0, 0.45, 0.22), size=2.4)
    look_at(rim, Vector((0, 0, 0.6)))
    sun = add_light("SunLamp", "SUN", (6, -2, 8), 2.1, (1.0, 0.78, 0.5), rot=(math.radians(40), math.radians(15), math.radians(25)))
    print("scene ready", [m.name for m in bpy.data.materials])


def build_character() -> None:
    root = bpy.data.objects.new("AmberRoot", None)
    _collection("Character").objects.link(root)
    root.empty_display_size = 0.3

    body = add_mesh("primitive_uv_sphere_add", "AmberBody", "Character", segments=32, ring_count=16, radius=1.0, location=(0.0, 0.0, 0.62))
    body.scale = (0.40, 0.34, 0.50)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(body, "Coral")
    bpy.ops.object.shade_smooth()
    body.parent = root

    belly = add_mesh("primitive_uv_sphere_add", "AmberBelly", "Character", segments=24, ring_count=12, radius=1.0, location=(0.10, -0.14, 0.46))
    belly.scale = (0.24, 0.15, 0.24)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(belly, "Belly")
    bpy.ops.object.shade_smooth()
    belly.parent = root

    eye = add_mesh("primitive_uv_sphere_add", "AmberEye", "Character", segments=20, ring_count=12, radius=0.10, location=(0.27, -0.20, 0.74))
    assign(eye, "Eye")
    bpy.ops.object.shade_smooth()
    eye.parent = root

    shine = add_mesh("primitive_uv_sphere_add", "AmberShine", "Character", segments=12, ring_count=8, radius=0.032, location=(0.32, -0.26, 0.78))
    assign(shine, "Shine")
    bpy.ops.object.shade_smooth()
    shine.parent = root

    for name, x in (("HipL", -0.13), ("HipR", 0.13)):
        hip = bpy.data.objects.new(name, None)
        _collection("Character").objects.link(hip)
        hip.location = (x, 0.02, 0.30)
        hip.empty_display_size = 0.08
        hip.parent = root
        leg = add_mesh(
            "primitive_cylinder_add",
            name.replace("Hip", "Leg"),
            "Character",
            vertices=16,
            radius=0.085,
            depth=0.30,
            location=(x, 0.02, 0.14),
        )
        assign(leg, "Coral")
        bpy.ops.object.shade_smooth()
        # keep world pose while parenting to hip
        leg.parent = hip
        leg.matrix_parent_inverse = hip.matrix_world.inverted()
        foot = add_mesh(
            "primitive_uv_sphere_add",
            name.replace("Hip", "Foot"),
            "Character",
            segments=12,
            ring_count=8,
            radius=0.09,
            location=(x + 0.03, 0.0, 0.03),
        )
        assign(foot, "Coral")
        bpy.ops.object.shade_smooth()
        foot.parent = hip
        foot.matrix_parent_inverse = hip.matrix_world.inverted()

    print("character built")


def pose_character(kind: str, phase: float) -> None:
    root = bpy.data.objects["AmberRoot"]
    hip_l = bpy.data.objects["HipL"]
    hip_r = bpy.data.objects["HipR"]
    body = bpy.data.objects["AmberBody"]

    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (0.0, 0.0, 0.0)
    body.scale = (1.0, 1.0, 1.0)
    hip_l.rotation_euler = (0.0, 0.0, 0.0)
    hip_r.rotation_euler = (0.0, 0.0, 0.0)

    if kind == "idle":
        bob = math.sin(phase * math.tau) * 0.018
        root.location.z = bob
        body.scale = (1.0 + bob * 0.8, 1.0 + bob * 0.4, 1.0 - bob * 1.4)
    elif kind == "run":
        swing = math.sin(phase * math.tau) * 0.62
        hip_l.rotation_euler.y = swing
        hip_r.rotation_euler.y = -swing
        root.location.z = abs(math.sin(phase * math.tau)) * 0.055
        body.scale = (1.02, 1.0, 0.96 + abs(math.sin(phase * math.tau)) * 0.05)
    elif kind == "jump":
        hip_l.rotation_euler.y = 0.55
        hip_r.rotation_euler.y = 0.35
        root.location.z = 0.04
        body.scale = (0.94, 1.0, 1.12)
    bpy.context.view_layer.update()


def build_props() -> None:
    coin = add_mesh("primitive_cylinder_add", "Coin", "Props", vertices=32, radius=0.34, depth=0.08, location=(0, 0, 0.34))
    coin.rotation_euler = (math.radians(90), 0.0, math.radians(18))
    assign(coin, "Gold")
    bpy.ops.object.shade_smooth()
    rim = add_mesh("primitive_torus_add", "CoinRim", "Props", major_radius=0.34, minor_radius=0.035, major_segments=32, minor_segments=12, location=(0, 0, 0.34))
    rim.rotation_euler = (math.radians(90), 0.0, math.radians(18))
    assign(rim, "Gold")
    bpy.ops.object.shade_smooth()

    plat = add_mesh("primitive_cube_add", "Platform", "Props", size=1.0, location=(0, 0, 0.12))
    plat.scale = (1.70, 0.55, 0.24)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(plat, "Stone")
    top = add_mesh("primitive_cube_add", "PlatformTop", "Props", size=1.0, location=(0, 0, 0.26))
    top.scale = (1.74, 0.58, 0.055)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(top, "AmberRim")

    wide = add_mesh("primitive_cube_add", "PlatformWide", "Props", size=1.0, location=(0, 0, 0.12))
    wide.scale = (2.20, 0.55, 0.24)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(wide, "Stone")
    wide_top = add_mesh("primitive_cube_add", "PlatformWideTop", "Props", size=1.0, location=(0, 0, 0.26))
    wide_top.scale = (2.24, 0.58, 0.055)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(wide_top, "AmberRim")

    ground = add_mesh("primitive_cube_add", "GroundBlock", "Props", size=1.0, location=(0, 0, -0.15))
    ground.scale = (3.4, 0.9, 0.55)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(ground, "Ground")
    grim = add_mesh("primitive_cube_add", "GroundRim", "Props", size=1.0, location=(0, 0, 0.14))
    grim.scale = (3.42, 0.92, 0.06)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(grim, "GroundRim")

    pole = add_mesh("primitive_cylinder_add", "FlagPole", "Props", vertices=12, radius=0.035, depth=1.15, location=(0.0, 0.0, 0.70))
    assign(pole, "Pole")
    banner = add_mesh("primitive_cube_add", "FlagBanner", "Props", size=1.0, location=(0.28, 0.0, 1.08))
    banner.scale = (0.48, 0.04, 0.28)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(banner, "Banner")
    print("props built")


def build_backdrop() -> None:
    # Sky dome (inverted sphere)
    dome = add_mesh("primitive_uv_sphere_add", "SkyDome", "Backdrop", segments=48, ring_count=24, radius=18.0, location=(0, 0, 0))
    bpy.ops.object.shade_smooth()
    mat = bpy.data.materials.new("SkyGrad")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bg = nt.nodes.new("ShaderNodeBackground")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.28
    ramp.color_ramp.elements[0].color = (0.95, 0.55, 0.24, 1)
    mid = ramp.color_ramp.elements.new(0.48)
    mid.color = (0.72, 0.26, 0.22, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (0.08, 0.06, 0.16, 1)
    nt.links.new(coord.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    dome.data.materials.append(mat)
    # flip normals so we see the inside
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")

    sun = add_mesh("primitive_uv_sphere_add", "SunBall", "Backdrop", segments=32, ring_count=16, radius=1.15, location=(6.4, -4.2, 5.6))
    assign(sun, "Sun")
    bpy.ops.object.shade_smooth()

    for i, (loc, scale) in enumerate(
        (
            ((-7.0, 2.5, 0.2), (5.5, 2.2, 2.4)),
            ((-1.5, 3.4, -0.1), (4.2, 1.8, 1.9)),
            ((4.8, 3.0, 0.0), (5.0, 2.0, 2.2)),
            ((9.5, 2.8, -0.2), (3.6, 1.6, 1.7)),
        )
    ):
        hill = add_mesh("primitive_ico_sphere_add", f"Hill_{i+1}", "Backdrop", subdivisions=3, radius=1.0, location=loc)
        hill.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        assign(hill, "Hill")
        bpy.ops.object.shade_smooth()
    print("backdrop built")


def aim_sprite_cam(target: Vector, scale: float, loc: Vector | None = None) -> None:
    cam = bpy.data.objects["SpriteCam"]
    if loc is None:
        loc = Vector((target.x + 1.15, target.y - 6.4, target.z + 0.73))
    cam.location = loc
    cam.data.ortho_scale = scale
    look_at(cam, target)
    bpy.context.scene.camera = cam


def render_still(path: Path, res=(512, 512), transparent: bool = True) -> None:
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]
    scene.render.film_transparent = transparent
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    scene.render.filepath = str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print("wrote", path, "exists", path.exists(), "bytes", path.stat().st_size if path.exists() else 0)


def save_blend() -> None:
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print("saved", BLEND)

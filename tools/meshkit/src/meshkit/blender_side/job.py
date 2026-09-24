"""meshkit's Blender-side job. Runs inside a headless Blender, never outside it.

    blender --background --factory-startup --python job.py -- \\
        --importer kinema_dae.py --site <meshkit site-packages> \\
        (--probe | --jobs jobs.json) --results results.json

For every job it:

1. starts from an empty scene,
2. imports the .dae with kinema's own COLLADA importer,
3. measures the imported geometry in world space,
4. exports those objects to a glTF binary at the job's *staging* path,
5. starts from an empty scene again and re-imports that GLB with Blender's glTF
   importer -- the path kinema takes when it meets a .glb --
6. measures again.

It only reports. Deciding whether the two measurements agree, and whether the
GLB may leave staging, is meshkit's job, outside Blender, where the comparison
is plain Python and can be unit-tested.

Results are rewritten after every job, so a crash half-way through a batch
still leaves an account of everything finished before it.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path

import bpy
import numpy as np


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(prog="meshkit-blender-job")
    parser.add_argument("--importer", required=True, type=Path)
    parser.add_argument("--site", required=True, type=Path,
                        help="meshkit's site-packages, for a pinned pycollada")
    parser.add_argument("--results", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--jobs", type=Path)
    mode.add_argument("--probe", action="store_true")
    return parser.parse_args(argv)


# --------------------------------------------------------------------- loading

def load_pinned_collada(site: Path):
    """Import pycollada from meshkit's environment, whatever else is on sys.path.

    A Blender profile with kinema installed already has a pycollada on sys.path
    (the extension's bundled wheel), and it survives --factory-startup. Which
    one wins would then depend on the machine. Loading the package from
    meshkit's own environment explicitly makes the version the one uv.lock pins.

    Only ``collada`` itself is taken from there. Its dependencies resolve
    normally, and meshkit's site-packages is *appended*, so Blender's own numpy
    keeps precedence over the copy in meshkit's environment.
    """
    package_dir = site / "collada"
    spec = importlib.util.spec_from_file_location(
        "collada", package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"no pycollada in {site}")
    if str(site) not in sys.path:
        sys.path.append(str(site))
    module = importlib.util.module_from_spec(spec)
    sys.modules["collada"] = module
    spec.loader.exec_module(module)
    return module


def load_importer(path: Path):
    """Load kinema's dae.py by path, without importing the kinema package."""
    spec = importlib.util.spec_from_file_location("meshkit_kinema_dae", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load importer from {path}")
    module = importlib.util.module_from_spec(spec)
    # Registered before executing, not after: dae.py defines @dataclass classes
    # under `from __future__ import annotations`, and dataclasses resolves their
    # annotations through sys.modules[cls.__module__]. An unregistered module
    # makes that lookup None and the import dies inside dataclasses.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- measurement

def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mesh_objects() -> list[bpy.types.Object]:
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]


def world_stats(objects: list[bpy.types.Object]) -> dict:
    """Triangle count, surface area, area-weighted centroid and AABB, in world space.

    Measured on the evaluated mesh with each object's world matrix applied, so a
    transform lost anywhere between import and re-import shows up as a moved
    centroid or a shifted box -- which is how the scattered-links failure of a
    naive OBJ conversion would have been caught.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    triangles: list[np.ndarray] = []
    materials: set[str] = set()
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            count = len(mesh.vertices)
            coords = np.empty(count * 3, dtype=np.float32)
            mesh.vertices.foreach_get("co", coords)
            coords = coords.reshape(-1, 3).astype(np.float64)
            matrix = np.array(obj.matrix_world, dtype=np.float64)
            world = coords @ matrix[:3, :3].T + matrix[:3, 3]
            tri_count = len(mesh.loop_triangles)
            indices = np.empty(tri_count * 3, dtype=np.int32)
            mesh.loop_triangles.foreach_get("vertices", indices)
            if tri_count:
                triangles.append(world[indices.reshape(-1, 3)])
        finally:
            evaluated.to_mesh_clear()
        for slot in obj.material_slots:
            if slot.material is not None:
                materials.add(slot.material.name)

    if not triangles:
        return {"objects": len(objects), "triangles": 0, "area": 0.0,
                "centroid": None, "aabb_min": None, "aabb_max": None,
                "materials": sorted(materials)}

    tris = np.concatenate(triangles)
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    area_each = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    area = float(area_each.sum())
    points = tris.reshape(-1, 3)
    if area > 0:
        centroid = (area_each[:, None] * (a + b + c) / 3.0).sum(axis=0) / area
    else:
        centroid = points.mean(axis=0)
    return {
        "objects": len(objects),
        "triangles": int(len(tris)),
        "area": area,
        "centroid": [float(v) for v in centroid],
        "aabb_min": [float(v) for v in points.min(axis=0)],
        "aabb_max": [float(v) for v in points.max(axis=0)],
        "materials": sorted(materials),
    }


# ------------------------------------------------------------------ gltf i/o

def _supported_kwargs(operator, wanted: dict) -> dict:
    """Keep only the keyword arguments this Blender's operator actually has.

    glTF operator options get renamed between Blender releases; passing an
    unknown one raises. Filtering keeps the job working across 5.x point
    releases, and the dropped names are reported rather than hidden.
    """
    known = set(operator.get_rna_type().properties.keys())
    return {key: value for key, value in wanted.items() if key in known}


EXPORT_OPTIONS = {
    "export_format": "GLB",
    "use_selection": True,
    "export_apply": True,
    "export_yup": True,          # glTF is Y-up by specification
    "export_texcoords": True,
    "export_normals": True,
    "export_materials": "EXPORT",
    "export_cameras": False,
    "export_lights": False,
    "export_animations": False,
    "export_extras": False,
}


def export_glb(objects: list[bpy.types.Object], output: Path) -> list[str]:
    operator = bpy.ops.export_scene.gltf
    kwargs = _supported_kwargs(operator, EXPORT_OPTIONS)
    dropped = sorted(set(EXPORT_OPTIONS) - set(kwargs))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    output.parent.mkdir(parents=True, exist_ok=True)
    operator(filepath=str(output), **kwargs)
    return dropped


def import_glb(path: Path) -> list[bpy.types.Object]:
    bpy.ops.import_scene.gltf(filepath=str(path))
    return mesh_objects()


# ------------------------------------------------------------------- the job

def run_one(importer, job: dict) -> dict:
    source = Path(job["source"])
    staged = Path(job["staged"])
    result: dict = {"id": job["id"], "source": str(source), "staged": str(staged)}
    started = time.perf_counter()
    try:
        reset_scene()
        imported = importer.import_dae(source)
        result["importer_warnings"] = list(imported.warnings)
        result["unit_meter"] = imported.unit_meter
        result["up_axis"] = imported.up_axis
        objects = list(imported.objects)
        if not objects:
            raise RuntimeError("the importer produced no geometry")
        result["source_stats"] = world_stats(objects)

        result["dropped_export_options"] = export_glb(objects, staged)
        if not staged.is_file():
            raise RuntimeError("the glTF exporter wrote no file")

        reset_scene()
        result["roundtrip_stats"] = world_stats(import_glb(staged))
        result["ok"] = True
    except Exception as exc:  # noqa: BLE001 - one bad file must not stop the batch
        result["ok"] = False
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    result["seconds"] = round(time.perf_counter() - started, 3)
    return result


def environment(collada) -> dict:
    return {
        "blender": bpy.app.version_string,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "collada_version": getattr(collada, "__version__", "unknown"),
        "collada_path": str(Path(collada.__file__).parent),
        "gltf_export": _has_operator("export_scene", "gltf"),
        "gltf_import": _has_operator("import_scene", "gltf"),
    }


def _has_operator(module: str, name: str) -> bool:
    try:
        getattr(getattr(bpy.ops, module), name).get_rna_type()
        return True
    except (AttributeError, KeyError):
        return False


def write(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    args = parse_args()
    collada = load_pinned_collada(args.site)
    importer = load_importer(args.importer)
    payload = {"environment": environment(collada), "results": []}

    if args.probe:
        write(args.results, payload)
        return 0

    jobs = json.loads(args.jobs.read_text(encoding="utf-8"))
    for job in jobs:
        payload["results"].append(run_one(importer, job))
        write(args.results, payload)
    write(args.results, payload)
    return 0


if __name__ == "__main__":
    # No sys.exit: background Blender exits on its own once the script returns,
    # and --python-exit-code already turns an uncaught exception into a
    # non-zero status. SystemExit inside a --python script is not something to
    # rely on across Blender releases.
    main()

import os, subprocess, sys, glob
from typing import Dict
from PIL import Image
import trimesh

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRIPOSR_DIR = os.path.join(BASE_DIR, "third_party", "TripoSR")

def ensure_triposr():
    if not os.path.exists(TRIPOSR_DIR):
        raise RuntimeError(
            "TripoSR not found. Please clone it into backend/third_party:\n"
            "  cd backend/third_party && git clone https://github.com/VAST-AI-Research/TripoSR.git\n"
            "Then install requirements in that folder: pip install -r requirements.txt"
        )

async def build_mesh_from_image(input_image: str, out_dir: str, bake_texture: bool = True, texture_resolution: int = 1024) -> Dict[str, str]:
    # Normalize filename
    img = Image.open(input_image).convert("RGB")
    norm_path = os.path.join(out_dir, "mesh_input.png")
    img.save(norm_path)

    # Run TripoSR
    cmd = [
        sys.executable, os.path.join(TRIPOSR_DIR, "run.py"),
        norm_path,
        "--output-dir", out_dir,
    ]
    if bake_texture:
        cmd += ["--bake-texture", "--texture-resolution", str(texture_resolution)]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"TripoSR failed:\n{proc.stdout}")

    # Find outputs (TripoSR typically writes mesh.obj and texture.png if baked)
    obj_candidates = glob.glob(os.path.join(out_dir, "*.obj"))
    ply_candidates = glob.glob(os.path.join(out_dir, "*.ply"))
    tex_candidates = glob.glob(os.path.join(out_dir, "*texture*.png")) + glob.glob(os.path.join(out_dir, "*albedo*.png"))

    mesh_obj = obj_candidates[0] if obj_candidates else None
    mesh_ply = ply_candidates[0] if ply_candidates else None

    # Convert to GLB for web viewing if we have an OBJ/PLY
    glb_path = None
    try:
        if mesh_obj:
            m = trimesh.load(mesh_obj, force='mesh')
        elif mesh_ply:
            m = trimesh.load(mesh_ply, force='mesh')
        else:
            m = None

        if m is not None:
            scene = trimesh.Scene(m)
            glb_bytes = trimesh.exchange.gltf.export_glb(scene)
            glb_path = os.path.join(out_dir, "model.glb")
            with open(glb_path, "wb") as f:
                f.write(glb_bytes)
    except Exception as e:
        # Don't fail the whole request if GLB export fails
        print("GLB export error:", e)

    out = {}
    if mesh_obj: out["obj"] = mesh_obj
    if mesh_ply: out["ply"] = mesh_ply
    if tex_candidates: out["texture"] = tex_candidates[0]
    if glb_path: out["glb"] = glb_path
    return out

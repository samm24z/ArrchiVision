from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import os, io, asyncio, shutil, subprocess, sys

from PIL import Image

from models.image_renderer import SketchRenderer
from models.three_d import build_mesh_from_image, ensure_triposr

API_PREFIX = "/api"

app = FastAPI(title="ArchiVision API", version="0.1.0")

# CORS for dev – tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ensure output dirs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Static files
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

renderer = SketchRenderer()

@app.get(API_PREFIX + "/health")
def health():
    return {"status": "ok"}

@app.post(API_PREFIX + "/render")
async def render_images(
    files: List[UploadFile] = File(...),
    prompt: str = Form("photorealistic exterior render, global illumination, ultra-detailed, 8k, award-winning architecture visualization"),
    negative_prompt: str = Form("people, text, logo, watermark"),
    num_images: int = Form(4),
    guidance_scale: float = Form(7.5),
    control_weight: float = Form(1.0),
    preprocessor: str = Form("lineart"), # "lineart" | "canny" | "none"
    seed: Optional[int] = Form(None),
):
    batch_id = str(uuid4())
    out_dir = os.path.join(OUTPUT_DIR, batch_id)
    os.makedirs(out_dir, exist_ok=True)

    saved = []
    for f in files:
        raw = await f.read()
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        in_path = os.path.join(out_dir, f"input_{f.filename}")
        img.save(in_path)
        saved.append(in_path)

    results = await renderer.render_batch(
        image_paths=saved,
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_images=num_images,
        guidance_scale=guidance_scale,
        control_weight=control_weight,
        preprocessor=preprocessor,
        seed=seed,
        out_dir=out_dir,
    )

    # Convert to public URLs (served by /outputs)
    public = [f"/outputs/{batch_id}/{os.path.basename(p)}" for p in results]
    return {"batch_id": batch_id, "images": public, "out_dir": f"/outputs/{batch_id}"}

@app.post(API_PREFIX + "/mesh")
async def mesh_from_sketch(
    file: UploadFile = File(...),
    bake_texture: bool = Form(True),
    texture_resolution: int = Form(1024),
):
    # Save upload
    batch_id = str(uuid4())
    out_dir = os.path.join(OUTPUT_DIR, batch_id)
    os.makedirs(out_dir, exist_ok=True)

    raw = await file.read()
    in_path = os.path.join(out_dir, f"mesh_input_{file.filename}")
    with open(in_path, "wb") as f:
        f.write(raw)

    # Ensure third_party/TripoSR exists
    ensure_triposr()

    # Build mesh
    mesh_paths = await build_mesh_from_image(
        input_image=in_path,
        out_dir=out_dir,
        bake_texture=bake_texture,
        texture_resolution=texture_resolution,
    )

    public = {k: f"/outputs/{batch_id}/{os.path.basename(v)}" for k, v in mesh_paths.items()}
    return {"batch_id": batch_id, "assets": public, "out_dir": f"/outputs/{batch_id}"}

# ArchiVision Backend (FastAPI + Diffusers + TripoSR)

## Features
- Sketch ➜ Render using Stable Diffusion 1.5 + ControlNet (lineart / canny).
- Image ➜ 3D using TripoSR, with optional texture baking and automatic GLB export for the web viewer.
- Simple REST API with static hosting of results under `/outputs`.

## Setup (Local, Python 3.10/3.11)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# (Optional, GPU) install CUDA build of torch that matches your driver
# See: https://pytorch.org/get-started/locally/
```

### Get TripoSR (for 3D endpoint)
```bash
cd backend/third_party
git clone https://github.com/VAST-AI-Research/TripoSR.git
cd TripoSR
pip install -r requirements.txt
# (If CUDA present and torchmcubes complains, see README troubleshooting)
```

### Run the API
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API will be at: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### Endpoints
- `POST /api/render` – form-data: `files` (1..N), `prompt`, `negative_prompt`, `num_images`, `guidance_scale`, `control_weight`, `preprocessor` (lineart|canny|none), `seed`  
  Returns list of generated image URLs.
- `POST /api/mesh` – form-data: `file`, `bake_texture` (bool), `texture_resolution` (int)  
  Returns URLs for `obj` / `ply` / `texture` / `glb` if available.

Outputs are hosted under `/outputs/{batch_id}/...`.

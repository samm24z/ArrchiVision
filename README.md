# ArchiVision – AI Renders & 3D from Architecture Sketches

An end-to-end web app:
- Upload raw building sketches ➜ generate multiple colorful renders (ControlNet + Stable Diffusion).
- Convert an image into a 3D mesh (TripoSR), view in browser, and download files.

## Quick Start (Local)
1. **Backend**
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate               # Windows: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   # (Optional, GPU) Install CUDA build of PyTorch from https://pytorch.org/get-started/locally/
   # TripoSR for 3D:
   cd third_party && git clone https://github.com/VAST-AI-Research/TripoSR.git && cd TripoSR && pip install -r requirements.txt
   cd ../../
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   echo 'NEXT_PUBLIC_API_URL=http://localhost:8000' > .env.local
   npm run dev
   ```
   Open http://localhost:3000

## One-Command with Docker (GPU-friendly)
```bash
docker compose up --build
```
> To forward an NVIDIA GPU, install `nvidia-container-toolkit` and your Docker will pass the GPU automatically on modern setups.

## Deploy Tips
- **Backend GPU**: Use a GPU VM (AWS g4dn.xlarge, g5.xlarge, Lambda Labs, Runpod). `git clone` the repo, `docker compose up -d`.
- **Frontend**: Can be hosted on Vercel/Netlify; set `NEXT_PUBLIC_API_URL` to your backend URL.
- **Model Downloads**: First run will download weights (~several GB). Persist `/backend/outputs` and cache dirs to speed up subsequent runs.

## API
- `POST /api/render` – multipart form with `files` (1..N). Optional fields: `prompt`, `negative_prompt`, `num_images`, `guidance_scale`, `control_weight`, `preprocessor` (lineart|canny|none), `seed`.
- `POST /api/mesh` – multipart form with `file`. Optional: `bake_texture` (bool), `texture_resolution`.

## Notes
- Results from sketches depend on line clarity. Try **lineart** preprocessor first; switch to **canny** for photographs or detailed scans.
- TripoSR yields **coarse** meshes good for visualization/blocking. For production CAD/BIM, export and refine in Blender/Revit/SketchUp.

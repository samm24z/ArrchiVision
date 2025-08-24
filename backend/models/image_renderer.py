import os, torch, numpy as np
from typing import List, Optional
from PIL import Image

from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from controlnet_aux import CannyDetector, LineartDetector

class SketchRenderer:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32

        # Base model (SD 1.5 for reliability on ControlNet 1.1)
        base_model_id = "runwayml/stable-diffusion-v1-5"

        # Default ControlNet – lineart works well for sketches; fall back to canny
        try:
            control_model_id = "lllyasviel/control_v11p_sd15_lineart"
            self.preferred = "lineart"
            self.controlnet = ControlNetModel.from_pretrained(control_model_id, torch_dtype=self.dtype)
        except Exception:
            control_model_id = "lllyasviel/control_v11p_sd15_canny"
            self.preferred = "canny"
            self.controlnet = ControlNetModel.from_pretrained(control_model_id, torch_dtype=self.dtype)

        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            base_model_id,
            controlnet=self.controlnet,
            torch_dtype=self.dtype,
            safety_checker=None, # architectures, not people; disable to avoid false positives
        )
        self.pipe.scheduler = UniPCMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.enable_attention_slicing()
        if self.device == "cuda":
            self.pipe = self.pipe.to("cuda")
            # try:
            #     self.pipe.enable_xformers_memory_efficient_attention()
            # except Exception:
            #     pass

        # Preprocessors
        self.canny = CannyDetector()
        self.line = LineartDetector.from_pretrained("lllyasviel/Annotators")

    async def render_batch(
        self,
        image_paths: List[str],
        prompt: str,
        negative_prompt: str,
        num_images: int,
        guidance_scale: float,
        control_weight: float,
        preprocessor: str,
        seed: Optional[int],
        out_dir: str,
    ) -> List[str]:
        rng = torch.Generator(device=self.device)
        if seed is not None:
            rng.manual_seed(seed)

        all_out = []
        for idx, pth in enumerate(image_paths):
            raw = Image.open(pth).convert("RGB")
            # Resize to 768 on the long edge for quality/perf balance
            raw = self._resize_max(raw, 768)

            if preprocessor == "lineart":
                cond = self.line(raw)
            elif preprocessor == "canny":
                cond = self.canny(raw, low_threshold=50, high_threshold=150)
            else:
                # If raw sketch already has clear edges, use it directly
                cond = raw

            images = self.pipe(
                prompt=[prompt] * num_images,
                negative_prompt=[negative_prompt] * num_images,
                image=[cond] * num_images,
                num_inference_steps=35,
                guidance_scale=guidance_scale,
                generator=rng,
                controlnet_conditioning_scale=control_weight,
            ).images

            for j, im in enumerate(images):
                out_path = os.path.join(out_dir, f"render_{idx}_{j}.png")
                im.save(out_path)
                all_out.append(out_path)

        return all_out

    def _resize_max(self, img: Image.Image, max_side: int) -> Image.Image:
        w, h = img.size
        if max(w, h) <= max_side: return img
        if w >= h:
            new_w = max_side
            new_h = int(h * max_side / w)
        else:
            new_h = max_side
            new_w = int(w * max_side / h)
        return img.resize((new_w, new_h), Image.LANCZOS)

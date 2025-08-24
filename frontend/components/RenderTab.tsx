'use client';
import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../lib/api';

type GenResponse = { batch_id: string; images: string[]; out_dir: string; };

export default function RenderTab(){
  const [files, setFiles] = useState<FileList|null>(null);
  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const [prompt, setPrompt] = useState("photorealistic exterior render, global illumination, ultra-detailed, 8k, award-winning architecture visualization");
  const [negative, setNegative] = useState("people, text, logo, watermark");
  const [num, setNum] = useState(4);
  const [guidance, setGuidance] = useState(7.5);
  const [control, setControl] = useState(1.0);
  const [preproc, setPreproc] = useState<'lineart'|'canny'|'none'>('lineart');

  const onUpload = async () => {
    if(!files || files.length===0) return;
    setLoading(true);
    try{
      const form = new FormData();
      Array.from(files).forEach(f=>form.append('files', f));
      form.append('prompt', prompt);
      form.append('negative_prompt', negative);
      form.append('num_images', String(num));
      form.append('guidance_scale', String(guidance));
      form.append('control_weight', String(control));
      form.append('preprocessor', preproc);

      const { data } = await axios.post<GenResponse>(`${API_URL}/api/render`, form, {
        headers: { 'Content-Type':'multipart/form-data' }
      });
      setImages(data.images.map(u => `${API_URL}${u}`));
    } catch(err:any){
      alert(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="grid md:grid-cols-2 gap-4">
        <div className="space-y-3">
          <input type="file" multiple accept="image/*" onChange={e=>setFiles(e.target.files)} className="block w-full"/>
          <textarea className="w-full border rounded-xl p-2" rows={3} value={prompt} onChange={e=>setPrompt(e.target.value)}/>
          <input className="w-full border rounded-xl p-2" placeholder="negative prompt" value={negative} onChange={e=>setNegative(e.target.value)}/>
          <div className="grid grid-cols-2 gap-3">
            <label className="text-sm"># images per sketch
              <input type="number" className="w-full border rounded-xl p-2" value={num} onChange={e=>setNum(parseInt(e.target.value)||1)}/>
            </label>
            <label className="text-sm">Guidance scale
              <input type="number" step="0.5" className="w-full border rounded-xl p-2" value={guidance} onChange={e=>setGuidance(parseFloat(e.target.value)||7.5)}/>
            </label>
            <label className="text-sm">Control weight
              <input type="number" step="0.1" className="w-full border rounded-xl p-2" value={control} onChange={e=>setControl(parseFloat(e.target.value)||1.0)}/>
            </label>
            <label className="text-sm">Preprocessor
              <select className="w-full border rounded-xl p-2" value={preproc} onChange={e=>setPreproc(e.target.value as any)}>
                <option value="lineart">lineart</option>
                <option value="canny">canny</option>
                <option value="none">none</option>
              </select>
            </label>
          </div>
          <button onClick={onUpload} disabled={loading} className="px-4 py-2 rounded-2xl bg-black text-white">
            {loading ? 'Rendering…' : 'Generate renders'}
          </button>
        </div>
        <div className="min-h-[300px]">
          {images.length===0 ? <p className="text-sm opacity-70">Generated images will appear here.</p> : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {images.map((src, i)=>(
                <a key={i} href={src} target="_blank">
                  <img src={src} className="w-full h-40 object-cover rounded-xl border"/>
                </a>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';
import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../lib/api';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';

type MeshResp = { batch_id: string; assets: Record<string,string> };

function GLBViewer({ url }: { url: string }){
  // Next.js requires this hook to be used inside canvas
  // @ts-ignore
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}

export default function MeshTab(){
  const [file, setFile] = useState<File|null>(null);
  const [glbUrl, setGlbUrl] = useState<string|null>(null);
  const [meta, setMeta] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const onBuild = async () => {
    if(!file) return;
    setLoading(true);
    try{
      const form = new FormData();
      form.append('file', file);
      form.append('bake_texture', 'true');
      form.append('texture_resolution', '1024');
      const { data } = await axios.post<MeshResp>(`${API_URL}/api/mesh`, form, {
        headers: { 'Content-Type':'multipart/form-data' }
      });
      const glb = data.assets?.glb;
      setMeta(data.assets);
      setGlbUrl(glb ? `${API_URL}${glb}` : null);
    } catch(err:any){
      alert(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <input type="file" accept="image/*" onChange={e=>setFile(e.target.files?.[0]||null)} />
      <button onClick={onBuild} disabled={loading} className="px-4 py-2 rounded-2xl bg-black text-white">
        {loading ? 'Building…' : 'Build 3D model'}
      </button>

      {glbUrl ? (
        <div className="w-full h-[480px] border rounded-2xl overflow-hidden">
          <Canvas camera={{ position: [0, 0.5, 2], fov: 50 }}>
            {/* @ts-ignore */}
            <ambientLight />
            {/* @ts-ignore */}
            <directionalLight position={[2, 3, 4]} />
            <React.Suspense fallback={null}>
              <GLBViewer url={glbUrl}/>
            </React.Suspense>
            <OrbitControls enablePan enableRotate enableZoom />
          </Canvas>
        </div>
      ) : <p className="text-sm opacity-70">Upload a sketch or reference image of a building facade to generate a rough 3D model. A downloadable OBJ/GLB will also be produced.</p> }

      {meta && (
        <div className="text-xs">
          <p>Assets:</p>
          <ul className="list-disc pl-5">
            {Object.entries(meta).map(([k,v])=> (
              <li key={k}><a className="underline" href={`${API_URL}${v}`} target="_blank" rel="noreferrer">{k}</a></li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

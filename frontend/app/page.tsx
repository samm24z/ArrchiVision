'use client';
import React, { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import RenderTab from '../components/RenderTab';
import MeshTab from '../components/MeshTab';

export default function HomePage() {
  const [tab, setTab] = useState<'render'|'mesh'>('render');
  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl md:text-5xl font-bold mb-2">ArchiVision</h1>
        <p className="text-sm md:text-base mb-6">Upload architecture sketches ➜ get colorful renders and 3D models.</p>

        <div className="flex gap-2 mb-6">
          <button onClick={()=>setTab('render')} className={`px-4 py-2 rounded-2xl ${tab==='render'?'bg-black text-white':'bg-white'}`}>Render</button>
          <button onClick={()=>setTab('mesh')} className={`px-4 py-2 rounded-2xl ${tab==='mesh'?'bg-black text-white':'bg-white'}`}>3D Model</button>
        </div>

        <motion.div
          key={tab}
          initial={{opacity:0, y:10}}
          animate={{opacity:1, y:0}}
          transition={{duration:0.2}}
          className="bg-white rounded-2xl p-4 md:p-6 shadow-sm"
        >
          {tab==='render' ? <RenderTab/> : <MeshTab/>}
        </motion.div>
      </div>
    </main>
  );
}

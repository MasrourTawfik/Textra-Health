// src/components/Hero.jsx
import React from 'react';
import { Activity } from 'lucide-react';
import { content } from '../data/content';

const Hero = () => {
  const { hero } = content;
  
  return (
    <div className="relative bg-blue-600 text-white py-16">
      <div className="max-w-4xl mx-auto text-center px-4">
        <h1 className="text-4xl font-bold mb-4">{hero.title}</h1>
        <p className="text-xl mb-4">{hero.subtitle}</p>
        <p className="mb-8">{hero.description}</p>
        <Activity className="w-16 h-16 mx-auto text-blue-200 animate-pulse" />
      </div>
      <div className="absolute bottom-0 w-full h-16 bg-gradient-to-b from-transparent to-blue-50"></div>
    </div>
  );
};

export default Hero;
import React, { useState } from 'react';
import { Mail, Lock, AlertCircle } from 'lucide-react';
import { Button } from 'd:/NeuroOceans.ai/src/components/Button/Button';
import { Card } from 'd:/NeuroOceans.ai/src/components/Card';
import {  Eye, EyeOff, Globe, Code } from 'lucide-react';
import { verifyCredentials } from '../services/authService';
import type { User } from '../types';

export const Login: React.FC<{ onLoginSuccess: (user: User) => void }> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    // Call authentication service verification
    const result = verifyCredentials(email, password);

    if (result.success && result.user) {
      onLoginSuccess(result.user);
    } else {
      setErrorMessage(result.error || 'Authentication failed');
    }
  };

  return (
     <div className="h-screen w-full flex  bg-[#FAFAFA] font-sans overflow-hidden">
    {/* LEFT SIDE: Branding & Graphic */}
      <div className="w-1/2 h-full bg-[#F3F3FF] p-16 flex flex-col justify-between items-center ">
        {/* Top Branding Section */}
        <div className="z-10">
          <div className="flex items-center gap-2 mb-8">
            {/* Logo Icon */}
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-lg tracking-tighter">
              S
            </div>
            <span className="text-xl font-bold text-[#1E293B]">Sanestix</span>
          </div>
          
          <h1 className="text-3xl md:text-4xl font-bold text-indigo-600 mb-4">
            Web Scraper
          </h1>
          <p className="text-[#64748B] max-w-sm text-sm md:text-base leading-relaxed">
            Powerful web scraping platform to collect, organize and analyze data effortlessly.
          </p>
        </div>

        {/* Dynamic Graphic Mockup (Replicating the browser/code visual from the image) */}
        <div className="relative mt-12 md:mt-0 flex justify-center items-center scale-90 md:scale-100 origin-bottom-left">
          {/* Main Browser Box */}
          <div className="w-72 h-44 bg-white rounded-xl shadow-xl border border-slate-100 p-4 relative z-10 flex flex-col justify-between">
            <div className="flex gap-1.5 mb-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-400"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            </div>
            <div className="flex-1 flex items-center justify-start pl-4">
              <div className="w-16 h-16 rounded-full border-2 border-indigo-100 flex items-center justify-center text-indigo-500">
                <Globe className="w-8 h-8" />
              </div>
              <div className="ml-4 space-y-2 flex-1">
                <div className="h-2 w-24 bg-slate-100 rounded"></div>
                <div className="h-2 w-16 bg-slate-100 rounded"></div>
              </div>
            </div>
          </div>
 {/* Floating Code Tag Box */}
          <div className="absolute -bottom-4 -right-2 z-20 bg-indigo-600 text-white p-3.5 rounded-xl shadow-lg flex items-center justify-center">
            <Code className="w-6 h-6" />
          </div>
         

          {/* Abstract background decorative dots/circles */}
          <div className="absolute -left-6 -bottom-6 w-48 h-48 bg-indigo-100 rounded-full blur-3xl opacity-60 -z-10"></div>
          <div className="absolute grid grid-cols-3 gap-2 -left-10 bottom-12 opacity-30">
            {[...Array(9)].map((_, i) => (
              <span key={i} className="w-1.5 h-1.5 bg-slate-400 rounded-full"></span>
            ))}
          </div>
        </div>
      </div>
    <div className="w-full md:w-1/2 flex items-center justify-center p-8 md:p-16 bg-white">
        <div className="w-full max-w-md">
          <h2 className="text-2xl md:text-3xl font-bold text-[#1E293B] mb-1">
            Welcome Back!
          </h2>
          <p className="text-sm text-[#64748B] mb-8">
            Please sign in to your account
          </p>
  

      <form onSubmit={handleLogin} className="space-y-5 ">
        
      
      {/* Error Alert Box */}
      {errorMessage && (
        <div className="mb-4  w-full bg-red-50 border border-red-200 text-red-600 text-xs rounded-lg p-3 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
        <div>
              <label className="block text-sm font-semibold text-[#1E293B] mb-2">
                Email address
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Mail className="w-5 h-5" />
                </span>
            <input
              type="email"
              className="w-full pl-20 pr-4 py-2.5  border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-indigo-600"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
        </div>

        <div>
              <label className="block text-sm font-semibold text-[#1E293B] mb-2">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Lock className="w-5 h-5" />
                </span>
                
            <input
              type="password"
              className="w-full pl-20  pr-4 py-2  border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-indigo-600"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            /> <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
          </div>
        
        </div>
    {/* Forgot Password Link */}
            <div className="text-right">
              <a href="#" className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 transition-colors">
                Forgot password?
              </a>
            </div>
        <Button type="submit"  className=" w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 px-4 rounded-lg text-sm shadow-sm transition-colors duration-200 disabled:opacity-70 disabled:cursor-not-allowed mt-2">
          Sign In
        </Button> 
          <div className="text-center mt-6">
              <p className="text-xs text-[#10B981] font-medium">
                Don't have an account?{' '}
                <a href="#" className="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors">
                  Sign up
                </a>
              </p>
            </div>
      </form>
    </div>
    </div>
    </div>
  );
};
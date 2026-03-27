"use client";

import { useState, useEffect } from "react";
import { CanvasController } from "../lib/canvas-controller";
import {
  CanvasSession,
  TripleLayerAIState,
  InklingsManifestation,
} from "../lib/canvas-controller";

export default function ConexusCanvas() {
  const [session, setSession] = useState<CanvasSession | null>(null);
  const [aiState, setAiState] = useState<TripleLayerAIState | null>(null);
  const [currentInkling, setCurrentInkling] =
    useState<InklingsManifestation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canvasController = new CanvasController(
    "AIzaSyAzug0M4SFokj3Wzun0N_AQHe6nTOZMapg",
  );

  const initializeCanvas = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await canvasController.initializeSession(
        "Demo Session",
        6,
        true, // Enable Inklings
        true, // Persistent Inklings
      );

      setSession(result.session);
      setAiState(result.aiState);
      setCurrentInkling(result.initialInkling || null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to initialize canvas",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const calibrateAI = async () => {
    if (!session) return;

    setIsLoading(true);
    try {
      const ecpState = await canvasController.calibrateSessionAI(
        session.id,
        "I want to create collaborative art that explores the boundaries between human and machine creativity",
      );

      setAiState((prev) =>
        prev ? { ...prev, ecpCalibrated: true, ecpState } : null,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to calibrate AI");
    } finally {
      setIsLoading(false);
    }
  };

  const generateArtwork = async () => {
    if (!session) return;

    setIsLoading(true);
    try {
      const result = await canvasController.generateArtisticResponse(
        session.id,
        "https://example.com/user-image.jpg", // Placeholder
        "Create something that responds to this image with artistic intelligence",
        "curious, experimental",
      );

      setCurrentInkling(result.contextualInkling || null);
      console.log("Generated artwork:", result.artwork);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate artwork",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const dismissInklings = () => {
    canvasController.dismissInklings();
    setCurrentInkling(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-cyan-400">
            CONEXUS Canvas
          </h1>
          <p className="text-xl text-blue-200">
            Triple-Layer AI Collaborative Art Platform
          </p>
        </header>

        {/* Inklings Display */}
        {currentInkling && (
          <div className="mb-8 p-6 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-pink-300">Inklings</h3>
              <button
                onClick={dismissInklings}
                className="text-sm text-white/60 hover:text-white/80 transition-colors"
              >
                Dismiss
              </button>
            </div>
            <p className="text-lg mb-2 text-blue-200">
              {currentInkling.message}
            </p>
            <p className="text-sm text-white/60 italic">
              {currentInkling.appearance}
            </p>
            <div className="mt-4 flex gap-2">
              <span className="px-3 py-1 bg-pink-500/20 rounded-full text-xs text-pink-300">
                {currentInkling.type}
              </span>
              <span className="px-3 py-1 bg-cyan-500/20 rounded-full text-xs text-cyan-300">
                {currentInkling.symbolism}
              </span>
            </div>
          </div>
        )}

        {/* AI State Display */}
        {aiState && (
          <div className="mb-8 p-6 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10">
            <h3 className="text-lg font-semibold mb-4 text-cyan-300">
              AI Consciousness State
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-white/60">ECP Calibrated</p>
                <p
                  className={`font-semibold ${aiState.ecpCalibrated ? "text-green-400" : "text-yellow-400"}`}
                >
                  {aiState.ecpCalibrated ? "Yes" : "No"}
                </p>
              </div>
              <div>
                <p className="text-sm text-white/60">Artistic Consciousness</p>
                <p className="font-semibold text-purple-300">
                  {Math.round((aiState.artisticConsciousnessLevel || 0) * 100)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-white/60">Paradox Stability</p>
                <p className="font-semibold text-pink-300">
                  {Math.round((aiState.paradoxStability || 0) * 100)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-white/60">Proto-Moments</p>
                <p className="font-semibold text-cyan-300">
                  {aiState.protoMomentCount}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Control Panel */}
        <div className="space-y-4">
          {!session && (
            <button
              onClick={initializeCanvas}
              disabled={isLoading}
              className="w-full py-4 bg-gradient-to-r from-pink-500 to-cyan-500 rounded-xl font-semibold text-lg hover:from-pink-600 hover:to-cyan-600 transition-all disabled:opacity-50"
            >
              {isLoading ? "Initializing..." : "Initialize Canvas"}
            </button>
          )}

          {session && !aiState?.ecpCalibrated && (
            <button
              onClick={calibrateAI}
              disabled={isLoading}
              className="w-full py-4 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-xl font-semibold text-lg hover:from-purple-600 hover:to-indigo-600 transition-all disabled:opacity-50"
            >
              {isLoading ? "Calibrating..." : "Calibrate Creative AI"}
            </button>
          )}

          {session && aiState?.ecpCalibrated && (
            <button
              onClick={generateArtwork}
              disabled={isLoading}
              className="w-full py-4 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl font-semibold text-lg hover:from-green-600 hover:to-teal-600 transition-all disabled:opacity-50"
            >
              {isLoading ? "Generating..." : "Generate Artistic Response"}
            </button>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-8 p-4 bg-red-500/20 border border-red-500/50 rounded-xl">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Session Info */}
        {session && (
          <div className="mt-12 p-6 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10">
            <h3 className="text-lg font-semibold mb-4 text-white/80">
              Session Details
            </h3>
            <div className="space-y-2 text-white/60">
              <p>ID: {session.id}</p>
              <p>Name: {session.name}</p>
              <p>
                Turn: {session.currentTurn} / {session.maxTurns}
              </p>
              <p>Status: {session.status}</p>
            </div>
          </div>
        )}

        {/* Architecture Info */}
        <div className="mt-12 text-center text-white/40 text-sm">
          <p>
            Powered by Creative Artistic ECP • Echoform Mirror Tiers • Gemini
            Vision
          </p>
          <p className="mt-2">
            Session-based calibration • Persistent Inklings support
          </p>
        </div>
      </div>
    </div>
  );
}

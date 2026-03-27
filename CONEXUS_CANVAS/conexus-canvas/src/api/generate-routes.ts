// CONEXUS Canvas Artistic Generation API
// Triple-layer AI artistic generation endpoints

import { NextRequest, NextResponse } from 'next/server';

// POST /api/canvas/generate - Generate artistic response with triple-layer AI
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      sessionId, 
      userImageUrl, 
      userPrompt, 
      emotionalContext = '' 
    } = body;

    if (!sessionId || !userImageUrl || !userPrompt) {
      return NextResponse.json(
        { error: 'Session ID, image URL, and prompt are required' },
        { status: 400 }
      );
    }

    // Import here to avoid module resolution issues
    const { CanvasController } = require('../lib/canvas-controller');
    const canvasController = new (CanvasController as any)(process.env.GEMINI_API_KEY);

    const result = await canvasController.generateArtisticResponse(
      sessionId,
      userImageUrl,
      userPrompt,
      emotionalContext
    );

    return NextResponse.json({
      success: true,
      data: {
        artwork: result.artwork,
        contextualInkling: result.contextualInkling,
        processingTime: result.artwork.metadata.processingTime,
        mirrorTier: result.artwork.mirrorTier,
        protoMoments: result.artwork.protoMoments
      }
    });

  } catch (error) {
    console.error('Artistic generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate artistic response' },
      { status: 500 }
    );
  }
}

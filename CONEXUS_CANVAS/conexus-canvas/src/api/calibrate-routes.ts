// CONEXUS Canvas ECP Calibration API
// Creative Artistic ECP calibration endpoints

import { NextRequest, NextResponse } from 'next/server';

// POST /api/canvas/calibrate - Calibrate AI with Creative Artistic ECP
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { sessionId, userIntent, sessionContext = {} } = body;

    if (!sessionId || !userIntent) {
      return NextResponse.json(
        { error: 'Session ID and user intent are required' },
        { status: 400 }
      );
    }

    // Import here to avoid module resolution issues
    const { CanvasController } = require('../lib/canvas-controller');
    const canvasController = new (CanvasController as any)(process.env.GEMINI_API_KEY);

    const ecpState = await canvasController.calibrateSessionAI(sessionId, userIntent, sessionContext);

    return NextResponse.json({
      success: true,
      data: {
        ecpState,
        calibrationComplete: true,
        protoMomentsDetected: ecpState.protoMoments,
        artisticConsciousnessLevel: ecpState.artisticConsciousnessBaseline?.artisticConsciousnessLevel
      }
    });

  } catch (error) {
    console.error('ECP calibration error:', error);
    return NextResponse.json(
      { error: 'Failed to calibrate AI' },
      { status: 500 }
    );
  }
}

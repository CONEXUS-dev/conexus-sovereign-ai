// CONEXUS Canvas API Routes
// Triple-layer AI integration endpoints

import { NextRequest, NextResponse } from 'next/server';
import { CanvasController } from '../lib/canvas-controller';

// Initialize controller with Gemini API key
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || 'AIzaSyAzug0M4SFokj3Wzun0N_AQHe6nTOZMapg';
const canvasController = new CanvasController(GEMINI_API_KEY);

// POST /api/canvas/session - Create new session
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { sessionName, maxTurns = 6, enableInklings = true, persistentInklings = false } = body;

    if (!sessionName) {
      return NextResponse.json(
        { error: 'Session name is required' },
        { status: 400 }
      );
    }

    const result = await canvasController.initializeSession(
      sessionName,
      maxTurns,
      enableInklings,
      persistentInklings
    );

    return NextResponse.json({
      success: true,
      data: result
    });

  } catch (error) {
    console.error('Session creation error:', error);
    return NextResponse.json(
      { error: 'Failed to create session' },
      { status: 500 }
    );
  }
}

// GET /api/canvas/session/:sessionId - Get session details
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('sessionId');

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      );
    }

    const session = canvasController.getSession(sessionId);
    const contributions = canvasController.getSessionContributions(sessionId);
    const aiState = canvasController.getAIState(sessionId);

    if (!session) {
      return NextResponse.json(
        { error: 'Session not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data: {
        session,
        contributions,
        aiState,
        inklingsState: canvasController.getInklingsState()
      }
    });

  } catch (error) {
    console.error('Session fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch session' },
      { status: 500 }
    );
  }
}

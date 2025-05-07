import { NextRequest, NextResponse } from 'next/server';

interface Feedback {
  message_index: number;
  feedback_text: string;
  rating: 'thumbs-up' | 'thumbs-down' | null;
  chroma_conversation_id: string;
  timestamp: string;
}

const feedbacks: Feedback[] = [];

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const requiredFields = ['message_index', 'feedback_text', 'chroma_conversation_id'];
    for (const field of requiredFields) {
      if (!(field in body)) {
        return NextResponse.json({ error: `Missing required field: ${field}` }, { status: 400 });
      }
      if (field === 'feedback_text' && (typeof body[field] !== 'string' || !body[field].trim())) {
        return NextResponse.json({ error: 'feedback_text must be a non-empty string' }, { status: 400 });
      }
    }

    const { message_index, feedback_text, rating, chroma_conversation_id } = body;

    if (!Number.isInteger(message_index)) {
      return NextResponse.json({ error: 'message_index must be an integer' }, { status: 400 });
    }

    if (body.hasOwnProperty('rating') && rating !== null && !['thumbs-up', 'thumbs-down'].includes(rating)) {
      return NextResponse.json(
        { error: "rating must be 'thumbs-up', 'thumbs-down', or null" },
        { status: 400 }
      );
    }


    if (typeof chroma_conversation_id !== 'string' || !chroma_conversation_id.trim()) {
      return NextResponse.json(
        { error: 'chroma_conversation_id must be a non-empty string' },
        { status: 400 }
      );
    }

    const feedbackEntry: Feedback = {
      message_index,
      feedback_text,
      rating: body.hasOwnProperty('rating') ? rating : null, 
      chroma_conversation_id,
      timestamp: new Date().toISOString(),
    };

    feedbacks.push(feedbackEntry);

    console.log('Received feedback:', feedbackEntry);

    return NextResponse.json({ message: 'Feedback submitted successfully' }, { status: 200 });
  } catch (error: unknown) {
    console.error('Error processing feedback:', error);
    if (error instanceof SyntaxError) {
        return NextResponse.json({ error: 'Invalid JSON payload' }, { status: 400 });
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET() {
  try {
    return NextResponse.json({ feedbacks, total: feedbacks.length }, { status: 200 });
  } catch (error: unknown) {
    console.error('Error retrieving feedbacks:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
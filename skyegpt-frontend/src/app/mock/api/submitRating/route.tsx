import { NextRequest, NextResponse } from 'next/server';

interface Rating {
  message_index: number;
  rating: 'thumbs-up' | 'thumbs-down';
  chroma_conversation_id: string;
  timestamp: string;
}

const ratings: Rating[] = [];

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const requiredFields = ['message_index', 'rating', 'chroma_conversation_id'];
    for (const field of requiredFields) {
      if (!(field in body)) {
        return NextResponse.json({ error: `Missing required field: ${field}` }, { status: 400 });
      }
    }

    const { message_index, rating, chroma_conversation_id } = body;

    if (!Number.isInteger(message_index)) {
      return NextResponse.json({ error: 'message_index must be an integer' }, { status: 400 });
    }
    if (!['thumbs-up', 'thumbs-down'].includes(rating)) {
      return NextResponse.json(
        { error: "rating must be 'thumbs-up' or 'thumbs-down'" },
        { status: 400 }
      );
    }

    if (typeof chroma_conversation_id !== 'string' || !chroma_conversation_id.trim()) {
      return NextResponse.json(
        { error: 'chroma_conversation_id must be a non-empty string' },
        { status: 400 }
      );
    }

    const ratingEntry: Rating = {
      message_index,
      rating,
      chroma_conversation_id,
      timestamp: new Date().toISOString(),
    };

    ratings.push(ratingEntry);

    console.log('Received rating:', ratingEntry);

    return NextResponse.json({ message: 'Rating submitted successfully' }, { status: 200 });
  } catch (error: unknown) {
    console.error('Error processing rating:', error);
    if (error instanceof SyntaxError) {
        return NextResponse.json({ error: 'Invalid JSON payload' }, { status: 400 });
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET() {
  try {
    return NextResponse.json({ ratings, total: ratings.length }, { status: 200 });
  } catch (error: unknown) {
    console.error('Error retrieving ratings:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
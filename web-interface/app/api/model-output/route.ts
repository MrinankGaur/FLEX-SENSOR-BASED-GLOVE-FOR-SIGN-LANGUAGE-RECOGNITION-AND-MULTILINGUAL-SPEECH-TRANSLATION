import { NextResponse } from 'next/server';

// In-memory store for the latest model output
// In production, you might want to use Redis or a database
let latestOutput: string = '';
let clients: Set<ReadableStreamDefaultController> = new Set();

// POST endpoint to receive model output
export async function POST(request: Request) {
  try {
    const { text } = await request.json();
    if (!text) {
      return NextResponse.json({ error: 'Missing "text" field' }, { status: 400 });
    }

    // Update the latest output
    latestOutput = text;

    // Broadcast to all connected clients
    const message = `data: ${JSON.stringify({ text })}\n\n`;
    clients.forEach((client) => {
      try {
        client.enqueue(new TextEncoder().encode(message));
      } catch (error) {
        // Client disconnected, remove it
        clients.delete(client);
      }
    });

    return NextResponse.json({ success: true, message: 'Output received and broadcasted' });
  } catch (error: any) {
    console.error('Error receiving model output:', error);
    return NextResponse.json({ error: `Failed to process output: ${error.message}` }, { status: 500 });
  }
}

// GET endpoint for Server-Sent Events
export async function GET(request: Request) {
  const stream = new ReadableStream({
    start(controller) {
      clients.add(controller);

      // Send the latest output immediately if available
      if (latestOutput) {
        const message = `data: ${JSON.stringify({ text: latestOutput })}\n\n`;
        controller.enqueue(new TextEncoder().encode(message));
      }

      // Keep connection alive
      const keepAlive = setInterval(() => {
        try {
          controller.enqueue(new TextEncoder().encode(': keepalive\n\n'));
        } catch (error) {
          clearInterval(keepAlive);
          clients.delete(controller);
        }
      }, 30000); // Send keepalive every 30 seconds

      // Clean up on close
      request.signal.addEventListener('abort', () => {
        clearInterval(keepAlive);
        clients.delete(controller);
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}


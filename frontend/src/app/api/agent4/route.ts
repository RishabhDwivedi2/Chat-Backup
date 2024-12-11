// AGENT 4

import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: NextRequest) {
  try {
    const { agent1Response, agent2Response, agent3Response } = await req.json(); // Parse the request body

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are an AI assistant that provides a summary of data visualized in a component." },
        { role: "user", content: `Summarize this data: ${JSON.stringify(agent3Response)}. It's visualized using a ${agent2Response.component} component. Initial context: ${agent1Response.content}` }
      ],
    });

    const summary = completion.choices[0].message.content;

    return NextResponse.json({ summary }); // Send the response
  } catch (error) {
    return NextResponse.json({ error: 'Error processing request' }, { status: 500 }); // Handle errors
  }
}
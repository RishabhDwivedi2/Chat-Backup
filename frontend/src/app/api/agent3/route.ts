import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        if (!body.message) {
            return NextResponse.json({ error: "Message is required" }, { status: 400 });
        }

        const { message } = body;

        // Temporary storage of the message (could be saved in a database if needed)
        console.log("Storing message temporarily:", message);

        const openaiResponse = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [
                { role: "system", content: "You are a helpful assistant." },
                { role: "user", content: message },
            ],
        });

        const responseData = openaiResponse.choices[0].message.content;

        // Immediate response from Agent1
        return NextResponse.json({
            content: responseData,
            component: "Text", // Placeholder component, modify as needed
        });
    } catch (error) {
        console.error("Error in Agent1:", error);
        return NextResponse.json({ error: "Agent 1 failed to process the message" }, { status: 500 });
    }
}

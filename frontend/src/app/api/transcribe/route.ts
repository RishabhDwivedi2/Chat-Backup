// File: src/app/api/transcribe/route.ts

import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import fs from 'fs';
import os from 'os';
import path from 'path';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: NextRequest) {
  let tempFilePath: string | null = null;

  try {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return NextResponse.json({ error: "File is required" }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    
    tempFilePath = path.join(os.tmpdir(), `upload-${Date.now()}.webm`);
    fs.writeFileSync(tempFilePath, buffer);

    const response = await openai.audio.transcriptions.create({
      file: fs.createReadStream(tempFilePath),
      model: "whisper-1",
    });

    return NextResponse.json({ transcript: response.text });
  } catch (error: any) {
    console.error("Error in API route:", error);
    return NextResponse.json({ error: "Error processing request", details: error.message }, { status: 500 });
  } finally {
    if (tempFilePath) {
      fs.unlinkSync(tempFilePath);
    }
  }
}
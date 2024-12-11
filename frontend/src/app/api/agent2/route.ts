// File: src/app/api/agent2/route.ts
// AGENT 2

import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

async function makeOpenAIRequest(messages: any[], retries = 3, delay = 1000) {
  for (let i = 0; i < retries; i++) {
    try {
      console.log(`Attempt ${i + 1}: Sending request to OpenAI API...`);
      const response = await openai.chat.completions.create({
        model: "gpt-4o-mini", 
        messages: messages,
      });
      console.log("OpenAI API request successful");
      return response;
    } catch (error: any) {
      console.error(`Attempt ${i + 1} failed:`, error);
      
      if (error.cause) {
        console.error("Underlying error:", error.cause);
      }
      
      if (error.code === 'ENOTFOUND') {
        console.error("DNS lookup failed. Check your internet connection and DNS settings.");
      } else if (error.code === 'ECONNREFUSED') {
        console.error("Connection refused. Check if there's a firewall blocking the connection.");
      }
      
      if (i === retries - 1) {
        console.error("All retry attempts exhausted");
        throw error;
      }
      
      console.warn(`Retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 2; 
    }
  }
  throw new Error('Max retries reached');
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        if (!body.content || !body.component) {
            return NextResponse.json({ error: "Content and component are required" }, { status: 400 });
        }

        const { content, component, chartType } = body;

        const prompt = `
            Based on the following content summary: "${content}", 
            the selected component: ${component},
            ${chartType ? `and the chart type: ${chartType},` : ''}
            generate a structured JSON response that can be directly used in the ${component} component.

            Use the following format for each component type:

            For Table: { 
                title: string,
                headers: string[], 
                rows: any[][],
                style: { titleColor?: string, headerColor?: string, cellColor?: string }
            }
            For Chart: { 
                title: string,
                chartType: '${chartType ? chartType : "Bar"}',
                labels: string[],
                datasets: { label: string, data: number[], color?: string | string[] }[],
                style: { chartBackgroundColor?: string, chartBorderColor?: string }
            }
            For Card: { 
                title: string,
                content: string | { [key: string]: string | string[] },
                style: { titleColor?: string, contentColor?: string }
            }
            For Text: { 
                text: string,
                style: { textColor?: string }
            }

            Ensure all required fields are included and contain appropriate, realistic data based on the content summary.
            The response should be in valid JSON format without any additional formatting or explanations.
            `;

        const messages = [
            { role: "system", content: "You are an AI assistant that structures data for UI components. Respond with valid JSON only, following the specified format for each component type." },
            { role: "user", content: prompt }
        ];

        const response = await makeOpenAIRequest(messages);
        const responseContent = response.choices[0].message?.content?.trim() || '';
        console.log("OpenAI2 Raw Response:", responseContent);

        const cleanedContent = responseContent.replace(/```json\n?|\n?```/g, '').trim();

        let structuredData;
        try {
            structuredData = JSON.parse(cleanedContent);
        } catch (parseError) {
            console.error("Error parsing JSON in openai2:", cleanedContent);
            return NextResponse.json({ error: "Invalid JSON response from OpenAI" }, { status: 500 });
        }

        console.log("OpenAI2 Parsed Response:", JSON.stringify(structuredData, null, 2));

        return NextResponse.json(structuredData);
    } catch (error: any) {
        console.error("Error in openai2 API route:", error);
        return NextResponse.json({ error: "Error structuring data", details: error.message }, { status: 500 });
    }
}
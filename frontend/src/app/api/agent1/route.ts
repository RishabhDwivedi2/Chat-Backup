// File: src/app/api/agent1/route.ts
// AGENT 1

import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import useDynamicProfileConfigStore from '@/store/dynamicProfileConfigStore';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const UI_COMPONENTS = ['Table', 'Chart', 'Card', 'Text'] as const;
type ComponentType = typeof UI_COMPONENTS[number];

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
    if (!body.message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    const { message } = body;

    const messages = [
        {
          role: "system",
          content: `You are an AI assistant that helps to select and format UI components for data visualization. 
          You must choose from these components: ${UI_COMPONENTS.join(', ')}. 
          For each chart, return dynamic and specific styles such as colors, thickness, radii, and more.
          
          If 'Chart' is selected, you must also choose the most appropriate chart type based on the data provided. 
          Chart types to choose from include: 'Bar', 'Line', 'Pie', 'Radar', 'Radial', 'Area'. 
          
          Respond with a JSON object containing:
            - 'content': a detailed summary (2-3 sentences) of the content to be presented, including key insights or trends,
            - 'component': the selected UI component (${UI_COMPONENTS.join(', ')}),
            - 'chartType' (only if 'Chart' is selected): the specific type of chart.
            - 'style': style properties such as color, font size, etc., that are dynamically generated for each chart type.
      
          Return specific style attributes for each chart type like:
            - For Bar: bar thickness, bar color, background color.
            - For Pie: slice colors, background color.
            - For Line: stroke width, stroke color, background color.
            - For Radial: inner radius, outer radius, bar colors.
          
          Ensure the 'content' field provides a comprehensive overview that can stand alone as an informative response.
          Do not include any extra text, explanations, or notes outside the JSON object.`,
        },
        { role: "user", content: message },
      ];

    const response = await makeOpenAIRequest(messages);
    const responseContent = response.choices[0].message?.content?.trim() || '';
    console.log("OpenAI Raw Response:", responseContent);

    const cleanedContent = responseContent.replace(/```json\n?|\n?```/g, '').trim();

    let parsedResponse;
    try {
      parsedResponse = JSON.parse(cleanedContent);
    } catch (parseError) {
      console.error("Error parsing JSON:", cleanedContent);
      return NextResponse.json({ error: "Invalid JSON response from OpenAI" }, { status: 500 });
    }

    console.log("OpenAI Parsed Response:", JSON.stringify(parsedResponse, null, 2));

    if (
      parsedResponse.content &&
      parsedResponse.component &&
      UI_COMPONENTS.includes(parsedResponse.component as ComponentType)
    ) {
      return NextResponse.json(parsedResponse);
    } else {
      console.error("Invalid response format:", parsedResponse);
      return NextResponse.json({ error: "Invalid response format" }, { status: 400 });
    }
  } catch (error: any) {
    console.error("Error in API route:", error);
    return NextResponse.json({ error: "Error processing request", details: error.message }, { status: 500 });
  }
}
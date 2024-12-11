// src/app/layout.tsx

import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { Metadata } from "next";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    template: '%s',
    default: 'Chat | Powered by AI',
  },
  description: "Chat is an AI-powered chatbot that uses the latest advancements in AI to provide you with the best chat experience.",
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light"> 
      <body className={inter.className}>
        {children}
        <Toaster />
      </body>
    </html>
  );
}


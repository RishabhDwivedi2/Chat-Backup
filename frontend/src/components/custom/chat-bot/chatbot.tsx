// "use client"

// import dynamic from 'next/dynamic'
// import { Brain, CornerDownLeft, File, Folder, Handshake, Mic, Moon, MoonIcon, Paperclip, PiggyBankIcon, Settings, X } from "lucide-react"
// import { Tooltip, TooltipProvider, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
// import { Button } from "@/components/ui/button"
// import { Label } from "@/components/ui/label"
// import { Textarea } from "@/components/ui/textarea"
// import { useState, useRef, useEffect } from "react"
// import { SpokeSpinner } from "../../ui/spinner"
// import ChatControls from "./chat-controls";
// import { Bank } from "@mynaui/icons-react"
// import { ChatHeader } from "./chat-header"
// import { ChatContainer } from "./chat-container"
// import ChatArtifacts from "./chat-artifacts"

// const AnimatedGridPattern = dynamic(() => import('@/components/magicui/animated-grid-pattern'), { ssr: false })

// interface UploadedFile extends File {
//     documentId: number;
// }

// const generateChatId = () => {
//     const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
//     let chatId = '';
//     for (let i = 0; i < 7; i++) {
//         chatId += characters.charAt(Math.floor(Math.random() * characters.length));
//     }
//     return chatId;
// };

// function Chatbot() {
//     const [messages, setMessages] = useState([
//         { role: "assistant", content: "Hello! How can I assist you today?" },
//     ]);
//     const [attachedFiles, setAttachedFiles] = useState<UploadedFile[]>([]);
//     const fileInputRef = useRef<HTMLInputElement | null>(null);
//     const chatIdRef = useRef<string | null>(null);
//     const chatbotContainerRef = useRef<HTMLDivElement | null>(null);
//     const [showChatControls, setShowChatControls] = useState(false);
//     const [showChatArtifacts, setShowChatArtifacts] = useState(false);
//     const [artifactsData, setArtifactsData] = useState<{ component: string, data: any } | null>(null);

//     const toggleChatControls = () => {
//         setShowChatControls(!showChatControls);
//         setShowChatArtifacts(false);
//     };

//     const handleShowArtifacts = () => {
//         setShowChatControls(false);
//         setShowChatArtifacts(true);
//     };

//     useEffect(() => {
//         if (!chatIdRef.current) {
//             const newChatId = generateChatId();
//             chatIdRef.current = newChatId;
//             console.log("Generated chat ID:", newChatId);
//         }
//     }, []);

//     return (
//         <TooltipProvider>
//             <div className="flex h-screen w-full font-poppins">
//                 <AnimatedGridPattern
//                     numSquares={30}
//                     maxOpacity={0.1}
//                     duration={3}
//                     repeatDelay={1}
//                     className="absolute inset-0 [mask-image:radial-gradient(500px_circle_at_center,white,transparent)]"
//                 />
//                 <div className="flex flex-col overflow-y-auto w-full">
//                     <ChatHeader toggleChatControls={toggleChatControls} />

//                     <main
//                         className={`chatbot-container flex flex-1 gap-4 overflow-auto p-4 ${showChatControls || showChatArtifacts ? 'lg:flex-row' : 'flex-col justify-center items-center'
//                             }`} ref={chatbotContainerRef}
//                     >
//                         <ChatContainer
//                             chatbotContainerRef={chatbotContainerRef}
//                             messages={messages}
//                             setMessages={setMessages}
//                             attachedFiles={attachedFiles}
//                             setAttachedFiles={setAttachedFiles}
//                             fileInputRef={fileInputRef}
//                             showChatControls={showChatControls}
//                             chatIdRef={chatIdRef}
//                             showChatArtifacts={showChatArtifacts}
//                             setShowChatArtifacts={setShowChatArtifacts}
//                             setArtifactsData={setArtifactsData}
//                             className={`flex-1 ${showChatArtifacts ? 'lg:w-1/2' : showChatControls ? 'lg:w-[70%]' : 'w-full'
//                                 }`}
//                         />

//                         {showChatControls && !showChatArtifacts && (
//                             <ChatControls
//                                 chats={[]}
//                                 onClose={() => setShowChatControls(false)}
//                                 onShowArtifacts={handleShowArtifacts}
//                                 className="lg:w-[30%] flex-shrink-0"
//                             />
//                         )}

//                         {showChatArtifacts && (
//                             <ChatArtifacts
//                                 onClose={() => {
//                                     setShowChatArtifacts(false);
//                                     setShowChatControls(true);
//                                 }}
//                                 className="lg:w-1/2 flex-shrink-0"
//                                 artifactsData={artifactsData || { component: 'Text', data: {} }} 
//                             />
//                         )}
//                     </main>
//                 </div>
//             </div>
//         </TooltipProvider>
//     )
// }

// export default dynamic(() => Promise.resolve(Chatbot), { ssr: false })

export default function Chatbot() {
    return <>
        Working...
    </>;
}
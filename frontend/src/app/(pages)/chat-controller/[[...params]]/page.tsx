import { Metadata } from 'next';
import { Header } from "@/components/custom/chat-controller/header";
import RetroGrid from '@/components/magicui/retro-grid';
import Manager from '@/components/custom/chat-controller/manager';
import Particles from '@/components/magicui/particles';

export const metadata: Metadata = {
    title: 'Processor | Chat Controller',
};

export default function ChatControllerPage({ params }: { params: { slug?: string[] } }) {
    return (
        <div className="relative w-full overflow-hidden font-poppins">
            <RetroGrid className="fixed inset-0 z-0" angle={65} />
            <div className="relative z-10 flex flex-col h-screen">
                <Header />
                <div className="flex-grow overflow-hidden">
                    <Manager />
                </div>
            </div>
        </div>
    );
}
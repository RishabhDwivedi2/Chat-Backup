'use client'

import { Box, CodeXml, Handshake, LaptopIcon, Lock, MoonIcon, Settings, SunIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useEffect, useState } from "react";
import HyperText from "@/components/magicui/hyper-text";
import BoxReveal from "@/components/magicui/box-reveal";
import GradualSpacing from "@/components/magicui/gradual-spacing";
import WordPullUp from "@/components/magicui/word-pull-up";
import ShinyButton from "@/components/magicui/shiny-button";
import { BorderBeam } from "@/components/magicui/border-beam";

export const Header = () => {
    const { theme, setTheme, resolvedTheme, systemTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const ThemeIcon = () => {
        if (!mounted) return <div className="w-5 h-5" />;
        if (resolvedTheme === "light") {
            return <SunIcon className="w-5 h-5" />;
        } else if (resolvedTheme === "dark") {
            return <MoonIcon className="w-5 h-5" />;
        } else if (theme === "system" && systemTheme === "light") {
            return <SunIcon className="w-5 h-5" />;
        } else if (theme === "system" && systemTheme === "dark") {
            return <MoonIcon className="w-5 h-5" />;
        } else {
            return <LaptopIcon className="w-5 h-5" />;
        }
    };

    return (
        <header className="sticky top-0 z-10 flex h-[57px] items-center gap-2 px-4 bg-white/30 backdrop-blur-lg">

            <div className="flex items-center gap-1">
                {/* <Box className="w-6 h-6 font-medium" /> */}
                {/* <HyperText text="Chat Controller" className="text-xl font-medium" /> */}
                {/* <GradualSpacing text="Chat Controller" className="text-xl font-medium font-poppins" /> */}
                {/* <WordPullUp words="Processor" className="font-medium text-xl" /> */}
                <ShinyButton text="//Processor" />
            </div>

            <div className="ml-auto flex items-center gap-1">
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <button className="p-2">
                            <ThemeIcon />
                        </button>
                    </DropdownMenuTrigger>
                    {mounted && (
                        <DropdownMenuContent align="end" className="w-56">
                            <DropdownMenuItem onClick={() => setTheme("light")}>
                                <SunIcon className="w-5 h-5 mr-2" />
                                Light
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => setTheme("dark")}>
                                <MoonIcon className="w-5 h-5 mr-2" />
                                Dark
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => setTheme("system")}>
                                <LaptopIcon className="w-5 h-5 mr-2" />
                                System Default
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    )}
                </DropdownMenu>

                <Button variant="ghost" size="icon">
                    <Settings className="w-5 h-5" />
                </Button>
            </div>
        </header>
    );
};

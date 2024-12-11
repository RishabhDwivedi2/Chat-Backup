import { Button } from "@/components/ui/button";
import BoxReveal from "@/components/magicui/box-reveal";
import GridPattern from "@/components/magicui/animated-grid-pattern";
import { cn } from "@/lib/utils";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";

const AnimatedGridPattern = dynamic(
    () => import("@/components/magicui/animated-grid-pattern"),
    { ssr: false }
);

export function Welcome() {
    const router = useRouter();

    const handleDiscoverMore = () => {
        router.push('/login')
    }
    return (
        <>
        <div className="flex items-center justify-center flex-col h-screen w-full overflow-hidden font-poppins">
            <AnimatedGridPattern
                numSquares={30}
                maxOpacity={0.1}
                duration={3}
                repeatDelay={1}
                className="absolute inset-0 [mask-image:radial-gradient(500px_circle_at_center,white,transparent)]"
            />
            <BoxReveal boxColor={"#5046e6"} duration={0.5}>
                <p className="text-[3.5rem] font-semibold">
                    Welcome to Chat<span className="text-[#5046e6]">.</span>
                </p>
            </BoxReveal>

            <BoxReveal boxColor={"#5046e6"} duration={0.5}>
                <h2 className="mt-[.5rem] text-[1rem]">
                    AI-driven Conversations{" "}
                    <span className="text-[#5046e6]">Reimagined</span>
                </h2>
            </BoxReveal>

            <BoxReveal boxColor={"#5046e6"} duration={0.5}>
                <div className="mt-6">
                <p>
                        Engage in intelligent, dynamic conversations through a sophisticated AI that processes text, images, and more. <br />
                        -&gt; Built on a foundation of advanced <span className="font-semibold text-[#5046e6]">Natural Language Processing (NLP)</span> and <span className="font-semibold text-[#5046e6]">Artificial Intelligence (AI)</span>. <br />
                        -&gt; Enjoy a seamless, intuitive user interface designed for fluid interaction. <br />
                        -&gt; Fully customizable and open-source, tailored for optimal user experience.
                    </p>
                </div>
            </BoxReveal>

            <BoxReveal boxColor={"#5046e6"} duration={0.5}>
                <Button onClick={handleDiscoverMore} className="mt-[1.6rem] bg-[#5046e6]">Discover More</Button>
            </BoxReveal>
        </div>
        </>
    );
}

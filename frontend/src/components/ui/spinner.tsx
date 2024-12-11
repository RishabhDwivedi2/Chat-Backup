import { cn } from "@/lib/utils";
// Install MynaUI Icons from mynaui.com/icons
import { Spinner } from "@mynaui/icons-react";

interface SpinnerProps {
    size?: string;
    color?: string;  
}

interface SizeProps {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    xxl: string;
}

interface FillProps {
    slate: string;
    blue: string;
    red: string;
    green: string;
    white: string;
}

interface StrokeProps {
    slate: string;
    blue: string;
    red: string;
    green: string;
    white: string;
}

const sizesClasses: SizeProps = {
    xs: "w-4 h-4",
    sm: "w-5 h-5",
    md: "w-6 h-6",
    lg: "w-8 h-8",
    xl: "w-20 h-20",
    xxl: "w-30 h-30",
};

const fillClasses: FillProps = {
    slate: "fill-slate-800",
    blue: "fill-blue-500",
    red: "fill-red-500",
    green: "fill-emerald-500",
    white: "fill-white",
};

const strokeClasses: StrokeProps = {
    slate: "stroke-slate-500",
    blue: "stroke-blue-500",
    red: "stroke-red-500",
    green: "stroke-emerald-500",
    white: "stroke-white",
};

// The SpokeSpinner for SVG-based Spinners
export const SpokeSpinner = ({
    size = "md",
    color = "slate",
}: SpinnerProps) => {
    const isCustomColor = !strokeClasses[color as keyof StrokeProps];

    return (
        <div aria-label="Loading..." role="status">
            <Spinner
                className={cn(
                    "animate-spin",
                    sizesClasses[size as keyof SizeProps],
                    !isCustomColor
                        ? strokeClasses[color as keyof StrokeProps]
                        : undefined
                )}
                style={isCustomColor ? { stroke: color } : undefined}  // Custom color handling
            />
        </div>
    );
};

// The RoundSpinner for more rounded spinners
export const RoundSpinner = ({
    size = "md",
    color = "slate",
}: SpinnerProps) => {
    const isCustomColor = !fillClasses[color as keyof FillProps];

    return (
        <div aria-label="Loading..." role="status">
            <svg
                className={cn(
                    "animate-spin",
                    sizesClasses[size as keyof SizeProps],
                    !isCustomColor
                        ? fillClasses[color as keyof FillProps]
                        : undefined
                )}
                viewBox="3 3 18 18"
                style={isCustomColor ? { fill: color } : undefined}  // Custom color handling
            >
                <path
                    className="opacity-20"
                    d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"
                ></path>
                <path d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"></path>
            </svg>
        </div>
    );
};


interface UpdatedSpinnerProps {
    className?: string;
  }
  
  export const UpdatedSpokeSpinner = ({ className }: UpdatedSpinnerProps) => {
    return (
      <div aria-label="Loading..." role="status">
        <Spinner 
          className={cn(
            "animate-spin text-[hsl(var(--foreground))]",
            className
          )}
        />
      </div>
    );
  };
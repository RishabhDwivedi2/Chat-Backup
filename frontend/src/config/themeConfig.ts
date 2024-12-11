// src/config/themeConfig.ts

export const themeColors = [
    { name: "Zinc", color: "#71717a" },
    { name: "Slate", color: "#64748b" },
    { name: "Stone", color: "#78716c" },
    { name: "Gray", color: "#6b7280" },
    { name: "Neutral", color: "#737373" },
    { name: "Red", color: "#ef4444" },
    { name: "Rose", color: "#f43f5e" },
    { name: "Orange", color: "#f97316" },
    { name: "Green", color: "#22c55e" },
    { name: "Blue", color: "#3b82f6" },
    { name: "Yellow", color: "#eab308" },
    { name: "Violet", color: "#8b5cf6" },
  ] as const;
  
  export const themeModes = ["Light", "Dark"] as const;
  
  export const removeThemeClasses = (element: HTMLElement) => {
    const colorClasses = themeColors.map(color => color.name.toLowerCase());
    const modeClasses = themeModes.map(mode => mode.toLowerCase());
    
    element.classList.remove(
      ...colorClasses,
      ...modeClasses
    );
  };
  
  // Types
  export type ThemeColor = (typeof themeColors)[number]["name"];
  export type ThemeMode = (typeof themeModes)[number];
  
  export const DEFAULT_THEME = {
    color: "Zinc",
    mode: "Light"
  } as const;
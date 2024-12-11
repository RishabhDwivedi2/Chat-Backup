// File: src/config/panelLayoutConfig.ts

import { UserProfile } from "@/config/profileConfig";

export const getLayoutProps = (
  profile: UserProfile,
  visiblePanels: number,
  showChatHistory: boolean,
  showChatArtifacts: boolean,
  showChatProcessor: boolean,
  showChatControls: boolean
) => {

  const chatHistoryWidth = showChatHistory ? "w-[20%]" : "w-0";

  if (!showChatArtifacts && !showChatProcessor && !showChatControls) {
    return {
      chatContainerWidth: "w-[70%] max-w-[70%]",
      chatArtifactsWidth: "w-0",
      chatProcessorWidth: "w-0",
      chatControlsWidth: "w-0",
      justifyContent: "justify-center",
      chatHistoryWidth,
    };
  }

  if (showChatArtifacts && !showChatProcessor && !showChatControls) {
    return {
      chatContainerWidth: "w-[50%] max-w-[50%]",
      chatArtifactsWidth: "w-[50%] max-w-[50%]",
      chatProcessorWidth: "w-0",
      chatControlsWidth: "w-0",
      justifyContent: "justify-between",
      chatHistoryWidth,
    };
  }

  const twoPanelsCondition = (showChatArtifacts && showChatProcessor) ||
    (showChatArtifacts && showChatControls) ||
    (showChatProcessor && showChatControls);

  if (twoPanelsCondition) {
    return {
      chatContainerWidth: "w-[35%] max-w-[35%]",
      chatArtifactsWidth: showChatArtifacts ? "w-[35%] max-w-[35%]" : "w-0",
      chatProcessorWidth: showChatProcessor ? "w-[35%] max-w-[35%]" : "w-0",
      chatControlsWidth: showChatControls ? "w-[35%] max-w-[35%]" : "w-0",
      justifyContent: "justify-between",
      chatHistoryWidth,
    };
  }

  if (showChatProcessor && !showChatArtifacts && !showChatControls) {
    return {
      chatContainerWidth: "w-[50%] max-w-[50%]",
      chatProcessorWidth: "w-[50%] max-w-[50%]",
      chatArtifactsWidth: "w-0",
      chatControlsWidth: "w-0",
      justifyContent: "justify-between",
      chatHistoryWidth,
    };
  }

  if (showChatControls && !showChatArtifacts && !showChatProcessor) {
    return {
      chatContainerWidth: "w-[65%] max-w-[65%]",
      chatControlsWidth: "w-[35%] max-w-[35%]",
      chatArtifactsWidth: "w-0",
      chatProcessorWidth: "w-0",
      justifyContent: "justify-between",
      chatHistoryWidth,
    };
  }

  return {
    chatContainerWidth: "w-[70%]",
    chatArtifactsWidth: showChatArtifacts ? "w-[30%]" : "w-0",
    chatProcessorWidth: showChatProcessor ? "w-[30%]" : "w-0",
    chatControlsWidth: showChatControls ? "w-[35%] max-w-[35%]" : "w-0",
    justifyContent: "justify-between",
    chatHistoryWidth,
  };
};

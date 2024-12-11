// File: src/store/processorStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ProcessorStep {
  name: string;
  duration: string;
  status: 'pending' | 'inProgress' | 'completed';
}

export interface ProcessorData {
  id: string;
  title: string;
  subtext: string;
  steps: ProcessorStep[];
  agent1Response: any;
  agent2Response: any;
}

interface ProcessorStore {
  analyses: ProcessorData[];
  addAnalysis: (analysis: ProcessorData) => void;
  updateAnalysis: (id: string, updateData: Partial<ProcessorData>) => void;
  updateStep: (analysisId: string, stepIndex: number, status: 'pending' | 'inProgress' | 'completed', duration?: string) => void;
  setAgent1Response: (analysisId: string, response: any) => void;
  setAgent2Response: (analysisId: string, response: any) => void;
  refreshAnalyses: () => void;
}

export const useProcessorStore = create<ProcessorStore>()(
  persist(
    (set, get) => ({
      analyses: [],
      addAnalysis: (analysis) => set((state) => ({ analyses: [analysis, ...state.analyses] })),
      updateAnalysis: (id, updatedAnalysis) => set((state) => ({
        analyses: state.analyses.map(analysis => 
          analysis.id === id ? { ...analysis, ...updatedAnalysis } : analysis
        )
      })),
      updateStep: (analysisId, stepIndex, status, duration) => set((state) => ({
        analyses: state.analyses.map(analysis => {
          if (analysis.id !== analysisId) return analysis;
          const newSteps = [...analysis.steps];
          newSteps[stepIndex] = { ...newSteps[stepIndex], status, ...(duration && { duration }) };
          return { ...analysis, steps: newSteps };
        })
      })),
      setAgent1Response: (analysisId, response) => set((state) => ({
        analyses: state.analyses.map(analysis => 
          analysis.id === analysisId ? { ...analysis, agent1Response: response } : analysis
        )
      })),
      setAgent2Response: (analysisId, response) => set((state) => ({
        analyses: state.analyses.map(analysis => 
          analysis.id === analysisId ? { ...analysis, agent2Response: response } : analysis
        )
      })),
      refreshAnalyses: () => {
        const storedData = localStorage.getItem('analysis-storage');
        if (storedData) {
          const parsedData = JSON.parse(storedData);
          if (parsedData.state && parsedData.state.analyses) {
            set({ analyses: parsedData.state.analyses });
          }
        }
      },
    }),
    {
      name: 'analysis-storage',
    }
  )
);
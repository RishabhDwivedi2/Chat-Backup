export interface AnalysisStep {
    name: string;
    duration: string;
    status: 'pending' | 'inProgress' | 'completed';
  }
  
  export interface Analysis {
    id: string;
    title: string;
    subtext: string;
    steps: AnalysisStep[];
    agent1Response: any | null;
    agent2Response: any | null;
  }
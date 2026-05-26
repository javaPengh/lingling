export interface MemorySnapshot {
  weakPointIds: string[];
  recentStates: string[];
  effectiveStrategies: string[];
  learningSummary: string;
}

export async function readMemory(): Promise<MemorySnapshot> {
  return {
    weakPointIds: [],
    recentStates: [],
    effectiveStrategies: [],
    learningSummary: ""
  };
}

export async function writeBackMemory(): Promise<void> {
  // T2-4 will implement the data model §5 write-back contract.
}

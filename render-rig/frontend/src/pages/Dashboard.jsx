import { useState } from "react";
import ChartGrid from "../components/ChartGrid";
import { useChartTasks } from "../hooks/useChartTasks";
import GenerateButtonContainer from "../components/GenerateButton/GenerateButtonContainer";
import HeaderContainer from "../components/Header/HeaderContainer";
import RunIdContainer from "../components/RunId/RunIdContainer";
import LogIdInputContainer from "../components/LogIdInput/LogIdInputContainer";

export default function Dashboard() {
  const [logId, setLogId] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const { runId, chartStatuses, generateCharts } = useChartTasks(logId);

const handleGenerate = async () => {
  setIsGenerating(true);
  try {
    await generateCharts();
  } finally {
    setIsGenerating(false);
  }
};


  return (
    <main className="text-white px-8 space-y-6">
      <HeaderContainer />
      <LogIdInputContainer value={logId} onChange={(e) => setLogId(e.target.value)} placeholder="1fc1b7b4-a68a-491b-8984-3234ed71be08" />
      <GenerateButtonContainer onGenerate={handleGenerate} isGenerating={isGenerating} />
      <RunIdContainer runId={runId} />
      <ChartGrid chartStatuses={chartStatuses} />
    </main>
  );
}

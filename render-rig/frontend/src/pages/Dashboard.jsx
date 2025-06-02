import { useState } from "react";
import Header from "../components/Header";
import ChartGrid from "../components/ChartGrid";
import LogIdInput from "../components/LogIdInput";
import GenerateButton from "../components/GenerateButton";
import RunId from "../components/RunId";
import { useChartTasks } from "../hooks/useChartTasks"; // Assuming it's in hooks/

export default function Dashboard() {
  const [logId, setLogId] = useState("");
  const { runId, chartStatuses, generateCharts } = useChartTasks(logId);

  const handleGenerate = () => {
    generateCharts();
  };

  return (
    <main className="text-white px-8 space-y-6">
      <Header />
      <LogIdInput value={logId} onChange={(e) => setLogId(e.target.value)} />
      <GenerateButton onClick={handleGenerate} />
      <RunId runId={runId} />
      <ChartGrid chartStatuses={chartStatuses} />
    </main>
  );
}

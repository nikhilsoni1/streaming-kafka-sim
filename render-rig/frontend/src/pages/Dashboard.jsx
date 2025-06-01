import { useState } from "react";
import Header from "../components/Header";
import ChartGrid from "../components/ChartGrid";
import LogIdInput from "../components/LogIdInput";
import GenerateButton from "../components/GenerateButton";
export default function Dashboard() {
  const [logId, setLogId] = useState("");

  const handleGenerate = () => {
    console.log("Generate chart for logId:", logId);
    // Add chart generation logic here
  };

  return (
    <main className="text-white px-8 space-y-6">
      <Header />
      <LogIdInput value={logId} onChange={(e) => setLogId(e.target.value)} />
      <GenerateButton onClick={handleGenerate} />
      <ChartGrid />
    </main>
  );
}

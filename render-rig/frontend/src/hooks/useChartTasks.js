import { useState, useEffect } from "react";
import { submitChartTask, getChartNames, getTaskStatus } from "../api/chartApi";
import { generateRunId } from "../utils/runId";

export function useChartTasks(logId) {
  const [runId, setRunId] = useState("");
  const [chartNames, setChartNames] = useState([]);
  const [chartStatuses, setChartStatuses] = useState([]);

  // Fetch chart names once on mount
  useEffect(() => {
    async function fetchChartList() {
      try {
        const names = await getChartNames();
        setChartNames(names);
      } catch (error) {
        console.error("Error fetching chart names:", error);
      }
    }

    fetchChartList();
  }, []);

  // Submit chart tasks one-by-one (fully async per chart)
  const generateCharts = () => {
    if (!logId.trim()) {
      alert("Please enter a Log ID first.");
      return;
    }

    const newRunId = generateRunId({ upper: true });
    setRunId(newRunId);
    setChartStatuses([]); // reset old statuses

    chartNames.forEach(async (chartName) => {
      try {
        const res = await submitChartTask({ runId: newRunId, logId, chartName });

        const taskEntry = {
          chartName,
          taskId: res.task_id,
          status: "loading",
          chartJson: null,
        };

        setChartStatuses((prev) => [...prev, taskEntry]);
      } catch (err) {
        console.error(`Failed to submit task for ${chartName}:`, err);
        setChartStatuses((prev) => [
          ...prev,
          {
            chartName,
            taskId: null,
            status: "failed",
            chartJson: null,
          },
        ]);
      }
    });
  };

  // Polling logic
  useEffect(() => {
    const interval = setInterval(() => {
      chartStatuses.forEach((entry, index) => {
        if (entry.status !== "loading" || !entry.taskId) return;

        getTaskStatus(entry.taskId)
          .then((res) => {
            if (res.task_status === "success" || res.task_status === "failed") {
              setChartStatuses((prev) =>
                prev.map((e, i) =>
                  i === index
                    ? {
                        ...e,
                        status: res.task_status,
                        chartJson: res.chart_json ? JSON.parse(res.chart_json) : null,
                      }
                    : e
                )
              );
            }
          })
          .catch((err) => {
            console.error(`Polling failed for ${entry.chartName}:`, err);
          });
      });
    }, 500);

    return () => clearInterval(interval);
  }, [chartStatuses]);

  return { runId, chartStatuses, generateCharts };
}

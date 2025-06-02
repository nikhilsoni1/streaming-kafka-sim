// Get the list of available charts
export async function getChartNames() {
  const res = await fetch("http://localhost:8000/charts");

  if (!res.ok) {
    throw new Error("Failed to fetch chart names");
  }

  return await res.json(); // should return: ["accel_xyz", "gyro_raw", ...]
}


// Submit chart generation task
export async function submitChartTask({ runId, logId, chartName }) {
  const url = `http://localhost:8000/v2/charts/${runId}/${logId}/${chartName}`;
  const res = await fetch(url, { method: "GET" });

  if (!res.ok) {
    throw new Error(`Failed to submit chart: ${chartName}`);
  }

  return await res.json(); // should return: { task_id: "..." }
}


// Poll status of a chart task
export async function getTaskStatus(taskId) {
  const res = await fetch(`http://localhost:8000/v2/status/${taskId}`);

  if (!res.ok) {
    throw new Error("Failed to fetch task status");
  }

  return await res.json(); // should return: { task_status, chart_json }
}

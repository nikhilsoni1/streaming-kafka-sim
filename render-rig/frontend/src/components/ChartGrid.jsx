import Plot from "react-plotly.js";
import ChartBox from "./ChartBox";
import StatusIndicator from "./StatusIndicator";

export default function ChartGrid({ chartStatuses }) {
  console.log("ChartGrid chartStatuses:", chartStatuses[0]);

  return (
    <div className="grid grid-cols-2 gap-6 h-[80vh] overflow-y-auto pr-2">
      {chartStatuses.map((entry, i) => (
        <ChartBox key={entry.chartName || i} title={entry.chartName}>
          {entry.status === "loading" && <StatusIndicator status="loading" />}
          {entry.status === "failed" && <StatusIndicator status="failed" />}
          {entry.status === "success" && entry.chartJson && (
            <div className="w-full h-full">
              <Plot
                data={entry.chartJson.data}
                layout={{
                  ...entry.chartJson.layout,
                  autosize: true,
                  responsive: true,
                  paper_bgcolor: "#1e1e1e",
                  plot_bgcolor: "#1e1e1e",
                  font: { color: "#AAAAAA" },
                  margin: { l: 40, r: 10, t: 30, b: 80 }, // extra bottom margin
                  legend: {
                    orientation: "h",
                    x: 0.5,
                    y: -0.3,
                    xanchor: "center",
                    yanchor: "top",
                    font: { color: "#AAAAAA" },
                  },
                }}
                config={{ displayModeBar: false }}
                style={{ width: "100%", height: "100%" }}
                useResizeHandler={true}
              />
            </div>
          )}
        </ChartBox>
      ))}
    </div>
  );
}

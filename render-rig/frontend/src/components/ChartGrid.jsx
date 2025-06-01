import ChartBox from "./ChartBox";
import StatusIndicator from "./StatusIndicator";

const placeholderStatuses = [
  "loading", "success", "failed", "loading",
  "success", "failed", "success", "loading", "failed"
];

export default function ChartGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 h-[80vh] overflow-y-auto pr-2">
      {placeholderStatuses.map((status, i) => (
        <ChartBox key={i}>
          <StatusIndicator status={status} />
        </ChartBox>
      ))}
    </div>
  );
}

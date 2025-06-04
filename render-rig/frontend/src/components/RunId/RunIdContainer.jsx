// src/components/RunId/RunIdContainer.jsx
import RunId from '../RunId';

export default function RunIdContainer({ runId }) {
  if (!runId) return null; // Logic stays in the smart component

  return <RunId runId={runId} />;
}

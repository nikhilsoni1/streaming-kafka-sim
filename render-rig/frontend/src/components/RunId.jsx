// src/components/RunId.jsx
import React from "react";

export default function RunId({ runId }) {
  if (!runId) return null; // Don't render until runId exists

  return (
    <div className="font-inter text-[20px] text-[#AAAAAA]">
      RUN ID: {runId}
    </div>
  );
}

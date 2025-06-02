export default function GenerateButton({ onClick, disabled = false }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-[505px] h-[40px] rounded-[6px] border border-[#444444] bg-[#111111] text-[#777777] text-[20px] font-normal font-inter disabled:opacity-50 disabled:cursor-not-allowed"
    >
      Generate Chart
    </button>
  );
}

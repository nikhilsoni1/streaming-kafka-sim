import {
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/solid";

const STATUS_CONFIG = {
  loading: {
    icon: ArrowPathIcon,
    text: "Loading",
    color: "text-[#AAAAAA]",
    animation: "animate-spin",
  },
  success: {
    icon: CheckCircleIcon,
    text: "Success",
    color: "text-[#AAAAAA]",
    animation: "",
  },
  failed: {
    icon: XCircleIcon,
    text: "Failed",
    color: "text-[#AAAAAA]",
    animation: "",
  },
};

export default function StatusIndicator({ status = "loading" }) {
  const config = STATUS_CONFIG[status];
  const Icon = config.icon;

  return (
    <div
      className={`flex items-center gap-2 font-inter text-[20px] ${config.color}`}
      role="status"
      aria-live="polite"
    >
      <Icon
        className={`h-[20px] w-[20px] ${config.animation}`}
        aria-hidden="true"
      />
      <span className="leading-none">{config.text}</span>
    </div>
  );
}

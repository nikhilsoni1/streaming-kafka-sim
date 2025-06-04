import LogIdInput from "../LogIdInput";

export default function LogIdInputContainer({ value, onChange, placeholder }) {
  // No logic needed here for now, but structure is ready for future state/side-effects
  return <LogIdInput value={value} onChange={onChange} placeholder={placeholder} />;
}

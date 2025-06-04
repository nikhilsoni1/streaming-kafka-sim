export default function LogIdInput({ value, onChange, placeholder = "e.g. 1fc1b7b4-a68a-491b-8984-3234ed71be08" }) {
  return (
    <div className="space-y-2">
      <label className="block text-[#AAAAAA] text-[20px] font-medium font-inter">
        Log ID
      </label>
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-[505px] h-[40px] rounded-[6px] border border-[#444444] bg-[#111111] placeholder-[#777777] text-sm px-4 font-inter"
      />
    </div>
  );
}

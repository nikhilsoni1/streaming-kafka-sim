export default function ChartBox({ children, title }) {
  return (
    <div className="w-[756px] h-[336px] bg-[#1e1e1e] border border-[#444444] rounded-[8px] flex flex-col justify-between">
      
      {/* Chart or status content */}
      <div className="flex-1 flex items-center justify-center p-4 overflow-hidden">
        {children}
      </div>

      {/* Bottom title bar */}
      <div className="w-full h-[45px] bg-[#1e1e1e] border-t border-[#444444] rounded-b-[8px] flex items-center justify-center">
        <span className="font-inter font-medium text-[20px] text-[#AAAAAA] truncate">
          {title}
        </span>
      </div>
    </div>
  );
}

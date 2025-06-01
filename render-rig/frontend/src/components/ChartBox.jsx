export default function ChartBox({ children }) {
  return (
    <div className="w-[504px] h-[336px] bg-[#1e1e1e] border border-[#444444] rounded-[8px] flex flex-col justify-between">
      
      {/* Vertically center children */}
      <div className="flex-1 flex items-center justify-center">
        {children}
      </div>

      {/* Bottom strap line */}
      <div className="w-full h-[45px] bg-[#1e1e1e] border-t border-[#444444] rounded-b-[8px] flex items-center justify-center">
        <span className="font-inter font-medium text-[20px] text-[#AAAAAA]">
          Lorem Ipsum
        </span>
      </div>
    </div>
  );
}

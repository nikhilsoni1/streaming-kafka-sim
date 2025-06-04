// src/components/GenerateButton/GenerateButtonContainer.jsx
import GenerateButton from '../GenerateButton/GenerateButton';

export default function GenerateButtonContainer({ onGenerate, isGenerating }) {
  const handleClick = () => {
    if (onGenerate) onGenerate();
  };

  return <GenerateButton onClick={handleClick} disabled={isGenerating} />;
}

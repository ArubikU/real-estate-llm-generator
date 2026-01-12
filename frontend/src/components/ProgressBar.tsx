import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number; // 0-100
  status: string;
  stage?: string;
  substage?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ 
  progress, 
  status, 
  stage,
  substage 
}) => {
  const getStatusColor = () => {
    if (progress === 100) return '#10b981'; // green
    if (progress > 0) return '#3b82f6'; // blue
    return '#6b7280'; // gray
  };

  const getStageEmoji = () => {
    if (!stage) return '⏳';
    if (stage.includes('scraping') || stage.includes('fetching')) return '🌐';
    if (stage.includes('parsing') || stage.includes('extract')) return '🔍';
    if (stage.includes('llm') || stage.includes('ai')) return '🤖';
    if (stage.includes('embed')) return '📊';
    if (stage.includes('save') || stage.includes('storing')) return '💾';
    if (stage.includes('complete') || stage.includes('done')) return '✅';
    return '⏳';
  };

  return (
    <div className="progress-container">
      <div className="progress-header">
        <div className="progress-info">
          <span className="progress-emoji">{getStageEmoji()}</span>
          <div className="progress-text">
            <div className="progress-status">{status}</div>
            {stage && <div className="progress-stage">{stage}</div>}
            {substage && <div className="progress-substage">{substage}</div>}
          </div>
        </div>
        <div className="progress-percentage">
          {Math.round(progress)}%
        </div>
      </div>
      
      <div className="progress-bar-wrapper">
        <div 
          className="progress-bar-fill"
          style={{ 
            width: `${progress}%`,
            backgroundColor: getStatusColor(),
            transition: 'width 0.3s ease-out, background-color 0.3s ease'
          }}
        >
          <div className="progress-bar-shine"></div>
        </div>
      </div>
      
      {progress > 0 && progress < 100 && (
        <div className="progress-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      )}
    </div>
  );
};

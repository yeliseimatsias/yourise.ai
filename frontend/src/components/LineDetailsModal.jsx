import React from 'react';
import '../styles/LineDetailsModal.css';

const LineDetailsModal = ({ line, onClose }) => {
  if (!line) return null;

  // Определяем какой "цветовой" класс вешать на модалку
  // Если это старая колонка, тип будет 'purple', если новая - red/yellow/green
  const riskClass = line.type === 'purple' ? 'purple' : (line.risk || 'default');

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className={`modal-content modal-risk--${riskClass}`} 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
           <h3>Детали изменения</h3>
           <div className={`risk-badge risk-badge--${riskClass}`}>
             {riskClass === 'purple' ? 'Старая версия' : `Риск: ${riskClass}`}
           </div>
        </div>

        <div className="modal-body">
          
          <div className="modal-text-block">
            <strong>Текст:</strong>
            <p>{line.text}</p>
          </div>

          {line.explanation && (
            <div className="modal-info-section">
              <strong>Пояснение:</strong>
              <p>{line.explanation}</p>
            </div>
          )}

          {line.recommendation && (
            <div className="modal-info-section recommendation">
              <strong>Рекомендация:</strong>
              <p>{line.recommendation}</p>
            </div>
          )}
        </div>

        <button className="modal-close-btn" onClick={onClose}>Закрыть</button>
      </div>
    </div>
  );
};

export default LineDetailsModal;
import React from 'react';
import '../styles/LineDetailsModal.css';

const LineDetailsModal = ({ line, onClose }) => {
  if (!line) return null;

  // Определяем цветовой класс для стилизации модалки
  const getRiskClass = () => {
    if (line.type === 'purple') return 'purple';
    if (line.risk) {
      const r = line.risk.toLowerCase();
      if (r === 'red') return 'red';
      if (r === 'yellow') return 'yellow';
      if (r === 'green') return 'green';
    }
    return 'default';
  };

  const riskClass = getRiskClass();

  // Перевод риска на русский
  const getRiskLabel = () => {
    if (line.type === 'purple') return 'Старая версия';
    if (line.risk) {
      const r = line.risk.toLowerCase();
      if (r === 'red') return 'Красный';
      if (r === 'yellow') return 'Жёлтый';
      if (r === 'green') return 'Зелёный';
    }
    return 'Не определён';
  };

  // Определяем, есть ли у нас поля oldText/newText (изменение) или только text (строка документа)
  const hasChangeFields = line.oldText !== undefined || line.newText !== undefined;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className={`modal-content modal-risk--${riskClass}`} 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>Детали изменения</h3>
          <div className={`risk-badge risk-badge--${riskClass}`}>
            {getRiskLabel()}
          </div>
        </div>

        <div className="modal-body">
          {hasChangeFields ? (
            // Если это изменение из analysis
            <>
              {line.number && (
                <div className="modal-text-block">
                  <strong>Номер пункта:</strong>
                  <p>{line.number}</p>
                </div>
              )}
              {line.oldText && (
                <div className="modal-text-block">
                  <strong>Было:</strong>
                  <p>{line.oldText}</p>
                </div>
              )}
              {line.newText && (
                <div className="modal-text-block">
                  <strong>Стало:</strong>
                  <p>{line.newText}</p>
                </div>
              )}
            </>
          ) : (
            // Если это обычная строка документа (например, клик по строке без изменения)
            <div className="modal-text-block">
              <strong>Текст:</strong>
              <p>{line.text}</p>
            </div>
          )}

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

          {line.law_reference && (
            <div className="modal-info-section">
              <strong>Норма права:</strong>
              <p>{line.law_reference}</p>
            </div>
          )}

          {line.advice && (
            <div className="modal-info-section">
              <strong>Совет:</strong>
              <p>{line.advice}</p>
            </div>
          )}
        </div>

        <button className="modal-close-btn" onClick={onClose}>Закрыть</button>
      </div>
    </div>
  );
};

export default LineDetailsModal;
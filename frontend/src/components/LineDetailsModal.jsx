import React from 'react';
import '../styles/LineDetailsModal.css'; // можно создать отдельный файл стилей или использовать глобальные

const LineDetailsModal = ({ line, onClose }) => {
  if (!line) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3>Детали изменения</h3>
        {line.elementNumber && (
          <p><strong>Номер Статьи:</strong> {line.elementNumber}</p>
        )}
        <p><strong>Текст:</strong> {line.text}</p>
        {line.explanation && (
          <p><strong>Пояснение:</strong> {line.explanation}</p>
        )}
        {line.recommendation && (
          <p><strong>Рекомендация:</strong> {line.recommendation}</p>
        )}
        <button onClick={onClose}>Закрыть</button>
      </div>
    </div>
  );
};

export default LineDetailsModal;
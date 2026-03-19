import React, { useState, useRef, useEffect } from 'react';
import '../styles/RiskInfoButton.css';

const RiskInfoButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const buttonRef = useRef(null);
  const popupRef = useRef(null);

  const togglePopup = () => setIsOpen(!isOpen);

  // Закрытие при клике вне попапа
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        popupRef.current &&
        !popupRef.current.contains(event.target) &&
        !buttonRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="risk-info-button" ref={buttonRef}>
      <button className="question-button" onClick={togglePopup}>?</button>
      {isOpen && (
        <>
          <div className="popup-overlay" onClick={() => setIsOpen(false)} />
          <div className="popup" ref={popupRef}>
            <h3>Уровни риска</h3>
            <div className="risk-item">
              <span className="color-box purple" />
              <span><strong>Фиолетовый</strong> — Измененненая строка</span>
            </div>
            <div className="risk-item">
              <span className="color-box green" />
              <span><strong>Зеленый</strong> — Безопасно (стилистика/формат)</span>
            </div>
            <div className="risk-item">
              <span className="color-box yellow" />
              <span><strong>Желтый</strong> — Требует проверки (смысл изменился)</span>
            </div>
            <div className="risk-item">
              <span className="color-box red" />
              <span><strong>Красный</strong> — Потенциальное противоречие закону</span>
            </div>
            <button className="close-button" onClick={() => setIsOpen(false)}>Закрыть</button>
          </div>
        </>
      )}
    </div>
  );
};

export default RiskInfoButton;
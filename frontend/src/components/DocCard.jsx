import React from 'react';
import "../styles/DocCard.css";

const DocCard = ({
  title,
  file,
  contentLines,
  onLineClick,
  getChangeForLine,
  styleMode,           // 'old' или 'new'
  onLineHover,
  hoveredIndex,
  loading
}) => {
  const getRiskClass = (risk) => {
    if (!risk) return '';
    const r = risk.toLowerCase();
    if (r === 'red') return 'doc-line--red';
    if (r === 'yellow') return 'doc-line--yellow';
    if (r === 'green') return 'doc-line--green';
    return '';
  };

  const getLineClass = (change) => {
    if (!change) return '';
    if (styleMode === 'old') {
      // В старой колонке – фиолетовый для любых изменённых строк
      return 'doc-line--purple';
    } else {
      // В новой колонке – цвет по риску
      return getRiskClass(change.risk);
    }
  };

  return (
    <div className="doc-card">
      <div className="doc-card__header">
        <h3 className="doc-card__title">{title}</h3>
      </div>
      <div className="doc-card__content">
        {loading ? (
          <div className="doc-card__loading">Загрузка...</div>
        ) : (
          contentLines.map((line, idx) => {
            const change = getChangeForLine ? getChangeForLine(line) : null;
            const lineClass = getLineClass(change);
            const isHovered = hoveredIndex === idx;
            return (
              <div
                key={idx}
                className={`doc-line ${isHovered ? 'doc-line--hovered' : ''} ${lineClass}`}
                onClick={() => onLineClick(line)}
                onMouseEnter={() => onLineHover?.(idx)}
                onMouseLeave={() => onLineHover?.(null)}
              >
                {line.text}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default DocCard;
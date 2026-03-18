import '../styles/DocCard.css';

// Функция для получения CSS-класса по объекту строки
const getColorClass = (line) => {
  // Приоритет: риск (зелёный, жёлтый, красный, фиолетовый)
  if (line.risk) {
    switch (line.risk) {
      case 'green': return 'highlight-green';
      case 'yellow': return 'highlight-yellow';
      case 'red': return 'highlight-red';
      case 'purple': return 'highlight-purple';
      default: return '';
    }
  }
  // Иначе используем тип (например, для серого)
  switch (line.type) {
    case 'gray': return 'highlight-gray';
    default: return '';
  }
};

const DocCard = ({ 
  title, 
  articles, 
  file, 
  contentLines, 
  onLineClick, 
  onLineHover, 
  hoveredIndex,
  loading, 
  error 
}) => {
  return (
    <div className="doc-card">
      <h1 className="doc-card__main-title">{title}</h1>

      {contentLines && contentLines.length > 0 ? (
        <>
          {loading && <div className="doc-card__loading">Загрузка...</div>}
          {error && <div className="doc-card__error">{error}</div>}
          {!loading && !error && (
            <div className="doc-card__content">
              {contentLines.map((line, idx) => {
                const isEmpty = line.text.trim() === '';
                return (
                  <div
                    key={idx}
                    className={`doc-card__line ${
                      isEmpty 
                        ? 'doc-card__line--empty' 
                        : getColorClass(line)
                    } ${idx === hoveredIndex ? 'doc-card__line--hover' : ''}`}
                    onClick={() => !isEmpty && onLineClick && onLineClick(line)}
                    onMouseEnter={() => onLineHover && onLineHover(idx)}
                    onMouseLeave={() => onLineHover && onLineHover(null)}
                  >
                    {line.text || '\u00A0'}
                  </div>
                );
              })}
            </div>
          )}
        </>
      ) : file ? (
        <div className="doc-card__file-info">
          <p>Имя файла: {file.name}</p>
          <p>Размер: {(file.size / 1024).toFixed(2)} KB</p>
          {loading && <p>Чтение файла...</p>}
          {error && <p className="error">{error}</p>}
        </div>
      ) : articles ? (
        articles.map((article, index) => (
          <div key={index} className="doc-card__article">
            <h2 className="doc-card__article-title">{article.title}</h2>
            {article.paragraphs && article.paragraphs.length > 0 ? (
              <div className="doc-card__paragraphs">
                {article.paragraphs.map((paragraph, pIndex) => (
                  <p key={pIndex} className="doc-card__paragraph">{paragraph}</p>
                ))}
              </div>
            ) : (
              <p className="doc-card__empty"></p>
            )}
            {index < articles.length - 1 && <hr className="doc-card__separator" />}
          </div>
        ))
      ) : null}
    </div>
  );
};

export default DocCard;
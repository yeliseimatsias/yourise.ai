import '../styles/DocCard.css';

const getColorClass = (type) => {
  switch (type) {
    case 'green': return 'highlight-green';
    case 'yellow': return 'highlight-yellow';
    case 'red': return 'highlight-red';
    default: return '';
  }
};

const DocCard = ({ title, articles, file, contentLines, onLineClick, loading, error }) => {
  return (
    <div className="doc-card">
      <h1 className="doc-card__main-title">{title}</h1>

      {contentLines && contentLines.length > 0 && (
        <div className="doc-card__content">
          {loading && <div className="doc-card__loading">Загрузка...</div>}
          {error && <div className="doc-card__error">{error}</div>}
          {!loading && !error && contentLines.map((line, idx) => (
            <div
              key={idx}
              className={`doc-card__line ${getColorClass(line.type)}`}
              onClick={() => onLineClick && onLineClick(line)}
            >
              {line.text}
            </div>
          ))}
        </div>
      )}

      {file && !contentLines && (
        <div className="doc-card__file-info">
          <p>Имя файла: {file.name}</p>
          <p>Размер: {(file.size / 1024).toFixed(2)} KB</p>
          {loading && <p>Чтение файла...</p>}
          {error && <p className="error">{error}</p>}
        </div>
      )}

      {!file && !contentLines && articles?.map((article, index) => (
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
      ))}
    </div>
  );
};

export default DocCard;
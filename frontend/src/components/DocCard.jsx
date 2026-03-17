import '../styles/DocCard.css'; // подключим стили (опционально)

 
const DocCard = ({ title, articles }) => {
  return (
    <div className="doc-card">
      <h1 className="doc-card__main-title">{title}</h1>

      {articles.map((article, index) => (
        <div key={index} className="doc-card__article">
          <h2 className="doc-card__article-title">{article.title}</h2>

          {article.paragraphs && article.paragraphs.length > 0 ? (
            <div className="doc-card__paragraphs">
              {article.paragraphs.map((paragraph, pIndex) => (
                <p key={pIndex} className="doc-card__paragraph">
                  {paragraph}
                </p>
              ))}
            </div>
          ) : (
            // Если параграфов нет, можно ничего не выводить или поставить заглушку
            <p className="doc-card__empty"></p>
          )}

          {/* Разделитель между статьями (кроме последней) */}
          {index < articles.length - 1 && <hr className="doc-card__separator" />}
        </div>
      ))}
    </div>
  );
};

export default DocCard;
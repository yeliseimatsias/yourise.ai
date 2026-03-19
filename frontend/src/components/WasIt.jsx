import Title from "../components/Title"; // Проверь путь к компоненту, если он другой
import "../styles/WasIt.css";

const WasIt = ({ oldLines, newLines }) => {
  // 1. Проверка на загрузку данных
  if (!newLines || newLines.length === 0) {
    return (
      <section className="wasIt">
        <div className="wasIt__container container">
          <p className="wasIt__empty">Данные для таблицы загружаются...</p>
        </div>
      </section>
    );
  }

  // 2. Объект для маппинга русских названий и CSS классов
  const riskMap = {
    red: { label: "КРАСНЫЙ", class: "risk-red" },
    yellow: { label: "ЖЁЛТЫЙ", class: "risk-yellow" },
    green: { label: "ЗЕЛЁНЫЙ", class: "risk-green" },
    purple: { label: "ФИОЛЕТОВЫЙ", class: "risk-purple" },
  };

  // 3. Фильтруем только те строки, которые имеют риск (изменения)
  const changedData = newLines
    .map((newLine, index) => {
      if (newLine.risk !== null) {
        const art = newLine.article;
        
        // Умная сборка названия статьи: Статья + пункт + подпункт
        let articleFull = art?.title || "—";
        if (art?.clause) articleFull += `, п. ${art.clause}`;
        if (art?.subclause) articleFull += ` (${art.subclause})`;

        return {
          oldText: oldLines && oldLines[index] ? oldLines[index].text : "—",
          newText: newLine.text,
          articleTitle: articleFull,
          articleUrl: art?.url || null, // Сохраняем ссылку на НПА
          riskKey: newLine.risk,
          recommendation: newLine.recommendation || "—",
        };
      }
      return null;
    })
    .filter(item => item !== null);

  return (
    <section className="wasIt">
      <div className="wasIt__container container">
        <Title className="wasIt__title">Было – Стало</Title>
        
        {changedData.length === 0 ? (
          <p className="wasIt__empty">Изменений не обнаружено</p>
        ) : (
          <div className="wasIt__table-wrapper">
            <table className="wasIt__table">
              <thead>
                <tr>
                  <th width="5%">№</th>
                  <th width="25%">Было</th>
                  <th width="25%">Стало</th>
                  <th width="15%">Статья закона</th>
                  <th width="10%">Риск</th>
                  <th width="20%">Рекомендация</th>
                </tr>
              </thead>
              <tbody>
                {changedData.map((row, idx) => {
                  // Получаем данные о риске по ключу (red, yellow и т.д.)
                  const riskInfo = riskMap[row.riskKey] || { label: "—", class: "" };
                  
                  return (
                    <tr key={idx}>
                      {/* idx + 1 дает нам красивую нумерацию 1, 2, 3... */}
                      <td className="wasIt__cell-center">{idx + 1}</td>
                      
                      <td className="wasIt__text-cell wasIt__text-old">{row.oldText}</td>
                      <td className="wasIt__text-cell">{row.newText}</td>
                      
                      <td className="wasIt__article-cell">
                        {row.articleUrl ? (
                          <a 
                            href={row.articleUrl} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="wasIt__link"
                          >
                            {row.articleTitle}
                          </a>
                        ) : (
                          <span className="wasIt__no-link">{row.articleTitle}</span>
                        )}
                      </td>
                      
                      <td>
                        <span className={`wasIt__badge ${riskInfo.class}`}>
                          {riskInfo.label}
                        </span>
                      </td>
                      
                      <td className="wasIt__recommendation">{row.recommendation}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
};

export default WasIt;
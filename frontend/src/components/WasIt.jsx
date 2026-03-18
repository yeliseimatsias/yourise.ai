import Title from "./Title";
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
    red: { label: "КРАСНЫЙ", class: "risk-красный" },
    yellow: { label: "ЖЁЛТЫЙ", class: "risk-жёлтый" },
    green: { label: "ЗЕЛЁНЫЙ", class: "risk-зелёный" },
    purple: { label: "ФИОЛЕТОВЫЙ", class: "risk-фиолетовый" },
  };

  // 3. Фильтруем только те строки, которые были изменены или добавлены
  const changedData = newLines
    .map((newLine, index) => {
      // В вашем JSON изменения помечены типом 'modified' или 'added', либо наличием risk
      if (newLine.risk !== null) {
        return {
          пункт: index + 1,
          было: oldLines && oldLines[index] ? oldLines[index].text : "—",
          стало: newLine.text,
          статья: newLine.article?.title || "—",
          рискKey: newLine.risk, // например 'red'
          рекомендация: newLine.recommendation || "—",
          raw: newLine
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
                  <th>Пункт</th>
                  <th>Было</th>
                  <th>Стало</th>
                  <th>Статья закона</th>
                  <th>Риск</th>
                  <th>Рекомендация</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {changedData.map((row, idx) => {
                  const riskInfo = riskMap[row.рискKey] || { label: "—", class: "" };
                  
                  return (
                    <tr key={idx}>
                      <td>{row.пункт}</td>
                      <td className="wasIt__text-cell wasIt__text-old">{row.было}</td>
                      <td className="wasIt__text-cell">{row.стало}</td>
                      <td>{row.статья}</td>
                      <td className={riskInfo.class}>
                        {riskInfo.label}
                      </td>
                      <td>{row.рекомендация}</td>
                      <td>
                        <button 
                          className="details-button" 
                          onClick={() => console.log("Инфо:", row.raw)}
                        >
                          Подробнее
                        </button>
                      </td>
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
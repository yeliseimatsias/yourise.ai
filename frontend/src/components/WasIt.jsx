import Title from "../components/Title";
import "../styles/WasIt.css";

const WasIt = ({ changes, onRowClick }) => {
  const riskMap = {
    red: { label: "КРАСНЫЙ", class: "risk-red" },
    yellow: { label: "ЖЁЛТЫЙ", class: "risk-yellow" },
    green: { label: "ЗЕЛЁНЫЙ", class: "risk-green" },
    high: { label: "КРАСНЫЙ", class: "risk-red" },
    medium: { label: "ЖЁЛТЫЙ", class: "risk-yellow" },
    low: { label: "ЗЕЛЁНЫЙ", class: "risk-green" },
  };

  if (!changes || changes.length === 0) {
    return (
      <section className="wasIt">
        <div className="wasIt__container container">
          <p className="wasIt__empty">Изменений не обнаружено</p>
        </div>
      </section>
    );
  }

  const handleRowClick = (change) => {
    if (onRowClick) onRowClick(change);
  };

  return (
    <section className="wasIt">
      <div className="wasIt__container container">
        <Title className="wasIt__title">Было – Стало</Title>
        <div className="wasIt__table-wrapper">
          <table className="wasIt__table">
            <thead>
              <tr>
                <th width="5%">№</th>
                <th width="25%">Было</th>
                <th width="25%">Стало</th>
                <th width="15%">Пояснение</th>
                <th width="10%">Риск</th>
                <th width="20%">Рекомендация</th>
              </tr>
            </thead>
            <tbody>
              {changes.map((row, idx) => {
                const safeRiskKey = (row.risk || "").toLowerCase();
                const riskInfo = riskMap[safeRiskKey] || { label: "—", class: "" };
                return (
                  <tr
                    key={row.change_id || idx}
                    onClick={() => handleRowClick(row)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td className="wasIt__cell-center">{idx + 1}</td>
                    <td className="wasIt__text-cell wasIt__text-old">{row.oldText}</td>
                    <td className="wasIt__text-cell">{row.newText}</td>
                    <td className="wasIt__article-cell">{row.explanation}</td>
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
      </div>
    </section>
  );
};

export default WasIt;
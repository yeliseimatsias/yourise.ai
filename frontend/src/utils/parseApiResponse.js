export const parseApiResponse = ({ old_document, new_document, analysis }) => {
  // Функция для извлечения строк с нормализацией номера
  const getLines = (doc) => {
    if (!doc || !doc.elements) return [];
    return doc.elements.map((el, idx) => ({
      id: idx,
      text: el.content || el.title || '',
      type: el.type,
      number: el.number || el.elementNumber || null, // поддержка обоих полей
      level: el.level,
    }));
  };

  const oldLines = getLines(old_document);
  const newLines = getLines(new_document);

  // Собираем изменения из всех категорий риска
  const changes = [];
  const risks = analysis?.changes_by_risk || {};
  for (const [risk, items] of Object.entries(risks)) {
    items.forEach(item => {
      changes.push({
        change_id: item.change_id,
        number: item.number,
        old_number: item.old_number,
        type: item.type,
        oldText: item.old_text || '',
        newText: item.new_text || '',
        explanation: item.issue?.explanation || '',
        recommendation: item.issue?.suggestion || '',
        law_reference: item.issue?.law_reference,
        advice: item.issue?.advice,
        risk: risk,
        issue: item.issue ? { ...item.issue } : null,
      });
    });
  }

  const downloadLinks = analysis?.download_links || null;

  return { oldLines, newLines, changes, downloadLinks };
};
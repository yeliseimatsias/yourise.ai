export function parseApiResponse(apiResponse) {
  const { old_document, new_document, analysis } = apiResponse;

  /**
   * Группирует текст в блоки.
   * "Статья 1." -> Новый блок
   * "1. Текст..." -> Новый блок
   * Все, что не начинается с цифры или слова "Статья" -> приклеивается к текущему блоку
   */
  function groupIntoParagraphs(element) {
    const rawLines = element.content.split('\n').filter(line => line.trim() !== '');
    const paragraphs = [];
    let currentParagraph = null;

    rawLines.forEach(line => {
      const trimmed = line.trim();
      // Проверка на "1." или "2."
      const isNewNumberedPoint = /^\d+\./.test(trimmed);
      // Проверка на "Статья 1" или "Пункт 1"
      const isArticleHeader = /^(Статья|Пункт)\s+\d+/i.test(trimmed);

      if (isNewNumberedPoint || isArticleHeader) {
        if (currentParagraph !== null) {
          paragraphs.push(currentParagraph);
        }
        currentParagraph = line; 
      } else {
        if (currentParagraph === null) {
          currentParagraph = line;
        } else {
          // Склеиваем строки в один блок через пробел
          currentParagraph += ' ' + line;
        }
      }
    });

    if (currentParagraph !== null) {
      paragraphs.push(currentParagraph);
    }

    return paragraphs;
  }

  function elementToLines(element, docType) {
    const paragraphs = groupIntoParagraphs(element);
    return paragraphs.map((paragraph, idx) => ({
      text: paragraph,
      elementNumber: element.number,
      paragraphIndex: idx,
      sentenceIndex: 0,
      docType,
      type: 'unchanged',
      risk: null, // Изначально рисков нет
      recommendation: null,
      explanation: null,
    }));
  }

  let oldLines = [];
  old_document.elements.forEach(el => {
    oldLines = oldLines.concat(elementToLines(el, 'old'));
  });

  let newLines = [];
  new_document.elements.forEach(el => {
    newLines = newLines.concat(elementToLines(el, 'new'));
  });

  const changes = [];

  const findLine = (linesArray, elementNumber, textSubstring) => {
    if (!textSubstring) return null;
    const search = textSubstring.trim().toLowerCase();
    return linesArray.find(line => 
      line.elementNumber === elementNumber && 
      line.text.toLowerCase().includes(search)
    );
  };

  const riskColors = ['red', 'yellow', 'green'];
  
  riskColors.forEach(risk => {
    const changesList = analysis.changes_by_risk[risk] || [];
    
    changesList.forEach(change => {
      const { old_number, new_number, type, old_text, new_text, issue } = change;
      const changeType = type || 'modified';

      // 1. СТАРАЯ КОЛОНКА (СЛЕВА) - Делаем фиолетовым
      if (changeType === 'modified' || changeType === 'deleted') {
        const oldLine = findLine(oldLines, old_number, old_text);
        if (oldLine) {
          // Устанавливаем purple именно в risk, чтобы getColorClass в DocCard его поймал
          oldLine.risk = 'purple'; 
          oldLine.recommendation = issue?.suggestion;
          oldLine.explanation = issue?.explanation;
        }
      }

      // 2. НОВАЯ КОЛОНКА (СПРАВА) - Оставляем как было (red, yellow, green)
      if (changeType === 'modified' || changeType === 'added') {
        const newLine = findLine(newLines, new_number, new_text);
        if (newLine) {
          newLine.risk = risk; 
          newLine.recommendation = issue?.suggestion;
          newLine.explanation = issue?.explanation;
        }
      }

      changes.push({
        oldText: old_text || '—',
        newText: new_text || '—',
        explanation: issue?.explanation || '—',
        riskKey: risk,
        recommendation: issue?.suggestion || '—',
      });
    });
  });

  return { oldLines, newLines, changes };
}
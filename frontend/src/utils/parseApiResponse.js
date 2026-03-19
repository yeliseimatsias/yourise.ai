import { splitIntoSentences } from './textDiff';

export function parseApiResponse(apiResponse) {
  const { old_document, new_document, analysis } = apiResponse;

  /**
   * Группирует строки элемента в логические пункты.
   * Оставляет "Статья 1." отдельным блоком, а "1. ..." собирает 
   * вместе со всем последующим текстом до следующей цифры.
   */
  function groupIntoParagraphs(element) {
    const rawLines = element.content.split('\n').filter(line => line.trim() !== '');
    const paragraphs = [];
    let currentParagraph = null;

    rawLines.forEach(line => {
      const trimmed = line.trim();
      // Проверка на начало нового пункта: цифра, затем точка (например, "1.")
      const isNewNumberedPoint = /^\d+\./.test(trimmed);
      // Проверка на заголовок (например, "Статья 1.")
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
          // Склеиваем текст в один блок
          currentParagraph += ' ' + line;
        }
      }
    });

    if (currentParagraph !== null) {
      paragraphs.push(currentParagraph);
    }

    return paragraphs;
  }

  /**
   * Преобразует элемент в массив объектов-строк.
   * ВАЖНО: Больше не вызываем splitIntoSentences, чтобы не дробить пункты.
   */
  function elementToLines(element, docType) {
    const paragraphs = groupIntoParagraphs(element);
    return paragraphs.map((paragraph, idx) => ({
      text: paragraph,
      elementNumber: element.number,
      paragraphIndex: idx,
      sentenceIndex: 0,
      docType,
      type: 'unchanged',
      risk: null,
      recommendation: null,
      explanation: null,
    }));
  }

  // Собираем массивы строк
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
    return linesArray.find(line => 
      line.elementNumber === elementNumber && line.text.includes(textSubstring)
    );
  };

  // Обработка рисков и изменений
  const riskColors = ['red', 'yellow', 'green'];
  
  riskColors.forEach(risk => {
    const changesList = analysis.changes_by_risk[risk] || [];
    
    changesList.forEach(change => {
      const { old_number, new_number, type, old_text, new_text, issue } = change;
      const changeType = type || 'modified';

      // 1. Обработка старой колонки (делаем ФИОЛЕТОВЫМ)
      if (changeType === 'modified' || changeType === 'deleted') {
        const oldLine = findLine(oldLines, old_number, old_text);
        if (oldLine) {
          oldLine.type = 'changed-old'; // Этот тип привяжем к фиолетовому в CSS
          oldLine.risk = risk;
          oldLine.recommendation = issue?.suggestion;
          oldLine.explanation = issue?.explanation;
        }
      }

      // 2. Обработка новой колонки (оставляем цвета риска: красный/желтый/зеленый)
      if (changeType === 'modified' || changeType === 'added') {
        const newLine = findLine(newLines, new_number, new_text);
        if (newLine) {
          newLine.type = risk; 
          newLine.risk = risk;
          newLine.recommendation = issue?.suggestion;
          newLine.explanation = issue?.explanation;
        }
      }

      // 3. Общий список изменений для нижней панели
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
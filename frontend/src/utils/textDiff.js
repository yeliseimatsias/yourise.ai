// Разбивает текст на предложения (упрощённая версия)
export function splitIntoSentences(text) {
  // Ищем последовательности, заканчивающиеся .!? и пробелом или концом строки
  const sentences = text.match(/[^.!?]+[.!?]+(?:\s|$)/g);
  if (sentences && sentences.length > 0) {
    return sentences.map(s => s.trim());
  }
  // Если не удалось разбить, возвращаем весь текст как одно предложение
  return [text.trim()];
}
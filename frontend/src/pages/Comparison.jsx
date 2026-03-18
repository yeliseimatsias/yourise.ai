import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useFiles } from '../context/FileContext';
import Header from '../layouts/Header';
import Title from '../components/Title';
import DocCard from '../components/DocCard';
import { mockApiResponse } from '../mocks/mockApiResponse';
import "../styles/Comparison.css";

const Comparison = () => {
  const navigate = useNavigate();
  const { oldFile, newFile } = useFiles();

  const [oldLines, setOldLines] = useState([]);
  const [newLines, setNewLines] = useState([]);
  const [loading, setLoading] = useState({ old: false, new: false });
  const [error, setError] = useState({ old: '', new: '' });
  const [selectedLine, setSelectedLine] = useState(null);
  const [hoveredIndex, setHoveredIndex] = useState(null); // индекс строки, на которую наведён курсор

  useEffect(() => {
    if (!oldFile || !newFile) {
      navigate('/');
    }
  }, [oldFile, newFile, navigate]);

  // Симуляция загрузки старого файла (с фиолетовыми строками для изменённых)
  useEffect(() => {
    if (!oldFile) return;
    setLoading(prev => ({ ...prev, old: true }));
    
    // Создаём копию mockApiResponse, но заменяем текст на "старый" (для демо просто копируем текст)
    // и для строк, которые в mockApiResponse имеют риск (т.е. изменены), ставим risk: 'purple'
    const oldLinesData = mockApiResponse.map(item => {
      // Если у элемента есть риск (не null), значит строка была изменена в новой версии
      const isChanged = item.risk !== null;
      return {
        text: item.text, // В реальности здесь должен быть текст старого файла
        type: isChanged ? 'purple' : 'unchanged',
        risk: isChanged ? 'purple' : null,
        recommendation: null,
        article: null
      };
    });

    setTimeout(() => {
      setOldLines(oldLinesData);
      setLoading(prev => ({ ...prev, old: false }));
    }, 500);
  }, [oldFile]);

  // Используем мок-данные для новой редакции
  useEffect(() => {
    if (!newFile) return;
    setLoading(prev => ({ ...prev, new: true }));
    setTimeout(() => {
      setNewLines(mockApiResponse);
      setLoading(prev => ({ ...prev, new: false }));
    }, 500);
  }, [newFile]);

  const handleLineClick = (line) => {
    setSelectedLine(line);
  };

  const closeModal = () => setSelectedLine(null);

  if (!oldFile || !newFile) return null;

  return (
    <>
      <Header />
      <section className="compare_docs">
        <div className="compare_docs__container container">
          <Title className="compare_docs__title">Сравнение документов</Title>
          <div className="compare_docs__body">
            <DocCard
              title="Старая редакция"
              file={oldFile}
              contentLines={oldLines}
              onLineClick={handleLineClick}
              onLineHover={setHoveredIndex}   // передаём индекс при наведении
              hoveredIndex={hoveredIndex}      // передаём текущий индекс для подсветки
              loading={loading.old}
              error={error.old}
            />
            <DocCard
              title="Новая редакция"
              file={newFile}
              contentLines={newLines}
              onLineClick={handleLineClick}
              onLineHover={setHoveredIndex}
              hoveredIndex={hoveredIndex}
              loading={loading.new}
              error={error.new}
            />
          </div>
        </div>
      </section>

      {/* Модальное окно (без изменений) */}
      {selectedLine && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Детали изменения</h3>
            <p><strong>Текст:</strong> {selectedLine.text}</p>
            {selectedLine.recommendation && (
              <p><strong>Рекомендация:</strong> {selectedLine.recommendation}</p>
            )}
            {selectedLine.article && (
              <p>
                <strong>Статья:</strong> {selectedLine.article.title} —{' '}
                <a href={selectedLine.article.url} target="_blank" rel="noopener noreferrer">
                  открыть
                </a>
              </p>
            )}
            <button onClick={closeModal}>Закрыть</button>
          </div>
        </div>
      )}
    </>
  );
};

export default Comparison;
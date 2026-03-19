import { useNavigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { useFiles } from '../context/FileContext';
import Header from '../layouts/Header';
import Title from '../components/Title';
import DocCard from '../components/DocCard';
import { MOCK_API_RESPONSE } from '../mocks/mockApiResponse';
import { parseApiResponse } from '../utils/parseApiResponse';
import "../styles/Comparison.css";
import WasIt from '../components/WasIt';
import RiskInfoButton from '../layouts/RiskInfo';
import LineDetailsModal from '../components/LineDetailsModal';

const Comparison = () => {
  const navigate = useNavigate();
  const { oldFile, newFile } = useFiles();

  const [oldLines, setOldLines] = useState([]);
  const [newLines, setNewLines] = useState([]);
  const [changes, setChanges] = useState([]);
  const [loading, setLoading] = useState({ old: false, new: false });
  const [error, setError] = useState({ old: '', new: '' });
  const [selectedLine, setSelectedLine] = useState(null);
  const [hoveredIndex, setHoveredIndex] = useState(null);

  // ref и состояние для кнопки прокрутки
  const tableRef = useRef(null);
  const [isTableVisible, setIsTableVisible] = useState(false);

  useEffect(() => {
    if (!oldFile || !newFile) {
      navigate('/');
    }
  }, [oldFile, newFile, navigate]);

  useEffect(() => {
    if (!oldFile || !newFile) return;

    setLoading({ old: true, new: true });

    setTimeout(() => {
      try {
        const parsed = parseApiResponse(MOCK_API_RESPONSE);
        setOldLines(parsed.oldLines);
        setNewLines(parsed.newLines);
        setChanges(parsed.changes);
        setLoading({ old: false, new: false });
      } catch (err) {
        console.error(err);
        setError({ old: 'Ошибка загрузки', new: 'Ошибка загрузки' });
        setLoading({ old: false, new: false });
      }
    }, 500);
  }, [oldFile, newFile]);

  // Отслеживание видимости таблицы
  useEffect(() => {
    const handleScroll = () => {
      if (tableRef.current) {
        const rect = tableRef.current.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom >= 0;
        setIsTableVisible(isVisible);
      }
    };
    window.addEventListener('scroll', handleScroll);
    handleScroll(); // проверить сразу
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTable = () => {
    tableRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

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
              onLineHover={setHoveredIndex}
              hoveredIndex={hoveredIndex}
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

      {/* Оборачиваем WasIt в реф, чтобы отслеживать его положение */}
      <div ref={tableRef}>
        <WasIt changes={changes} />
      </div>

      <RiskInfoButton />

      {/* Кнопка прокрутки */}
      <button
        className={`scroll-button ${isTableVisible ? 'up' : 'down'}`}
        onClick={isTableVisible ? scrollToTop : scrollToTable}
        aria-label={isTableVisible ? 'Наверх' : 'К таблице'}
      >
        {isTableVisible ? '↑' : '↓'}
      </button>

      {selectedLine && (
        <LineDetailsModal line={selectedLine} onClose={closeModal} />
      )}
    </>
  );
};

export default Comparison;
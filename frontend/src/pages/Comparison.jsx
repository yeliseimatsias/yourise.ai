import { useNavigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { useFiles } from '../context/FileContext';
import Header from '../layouts/Header';
import Title from '../components/Title';
import DocCard from '../components/DocCard';
import { parseApiResponse } from '../utils/parseApiResponse';
import "../styles/Comparison.css";
import WasIt from '../components/WasIt';
import RiskInfoButton from '../layouts/RiskInfo';
import LineDetailsModal from '../components/LineDetailsModal';

const Comparison = () => {
  const navigate = useNavigate();
  const { oldFile, newFile, analysisData, setDownloadLinks } = useFiles();

  const [oldLines, setOldLines] = useState([]);
  const [newLines, setNewLines] = useState([]);
  const [changes, setChanges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedChange, setSelectedChange] = useState(null);
  const [hoveredIndex, setHoveredIndex] = useState(null);

  const tableRef = useRef(null);
  const [isTableVisible, setIsTableVisible] = useState(false);

  useEffect(() => {
    if (!analysisData) {
      navigate('/');
      return;
    }

    setLoading(true);
    try {
      const oldDoc = analysisData.old_document;
      const newDoc = analysisData.new_document;
      const analysis = analysisData.analysis;

      const result = parseApiResponse({
        old_document: oldDoc,
        new_document: newDoc,
        analysis: analysis,
      });

      setOldLines(result.oldLines);
      setNewLines(result.newLines);
      setChanges(result.changes || []);

      if (result.downloadLinks && setDownloadLinks) {
        setDownloadLinks(result.downloadLinks);
      }
    } catch (err) {
      console.error("Ошибка парсинга данных:", err);
    } finally {
      setLoading(false);
    }
  }, [analysisData, navigate, setDownloadLinks]);

  useEffect(() => {
    const handleScroll = () => {
      if (tableRef.current) {
        const rect = tableRef.current.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom >= 0;
        setIsTableVisible(isVisible);
      }
    };
    window.addEventListener('scroll', handleScroll);
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTable = () => {
    tableRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /// Поиск изменения для старой строки (фиолетовый цвет)
const findChangeForOldLine = (line) => {
  // 1. Если есть номер, ищем по номеру
  if (line.number) {
    let change = changes.find(c => c.old_number === line.number);
    if (change) return change;
    change = changes.find(c => c.type === 'deleted' && c.number === line.number);
    if (change) return change;
    change = changes.find(c => c.type === 'modified' && c.number === line.number);
    if (change) return change;
    change = changes.find(c => c.number === line.number && c.type !== 'added');
    if (change) return change;
  }

  // 2. Если номера нет, ищем по тексту (oldText)
  const trimmedText = line.text.trim();
  const changeByText = changes.find(c => c.oldText && c.oldText.trim() === trimmedText);
  if (changeByText) return changeByText;

  return null;
};

// Поиск изменения для новой строки (цвет по риску)
const findChangeForNewLine = (line) => {
  if (line.number) {
    let change = changes.find(c => c.number === line.number);
    if (change) return change;
    change = changes.find(c => c.type === 'moved' && c.old_number === line.number);
    if (change) return change;
  } else {
    // Если номера нет, ищем по тексту (newText)
    const trimmedText = line.text.trim();
    const changeByText = changes.find(c => c.newText && c.newText.trim() === trimmedText);
    if (changeByText) return changeByText;
  }
  return null;
};
  const handleLineClick = (line, change) => {
    if (change) {
      setSelectedChange(change);
    } else if (line.text && line.text.trim()) {
      setSelectedChange({
        ...line,
        risk: 'default',
        oldText: line.text,
        newText: line.text,
        explanation: 'Нет деталей анализа',
      });
    }
  };

  const closeModal = () => setSelectedChange(null);

  if (!oldFile || !newFile) return null;

  return (
    <>
      <Header />
      <section className="compare_docs">
        <div className="compare_docs__container container">
          <Title>Сравнение документов</Title>
          <div className="compare_docs__body">
            <DocCard
              title="Старая редакция"
              file={oldFile}
              contentLines={oldLines}
              onLineClick={(line) => handleLineClick(line, findChangeForOldLine(line))}
              getChangeForLine={findChangeForOldLine}
              styleMode="old"
              onLineHover={setHoveredIndex}
              hoveredIndex={hoveredIndex}
              loading={loading}
            />
            <DocCard
              title="Новая редакция"
              file={newFile}
              contentLines={newLines}
              onLineClick={(line) => handleLineClick(line, findChangeForNewLine(line))}
              getChangeForLine={findChangeForNewLine}
              styleMode="new"
              onLineHover={setHoveredIndex}
              hoveredIndex={hoveredIndex}
              loading={loading}
            />
          </div>
        </div>
      </section>

      <div ref={tableRef}>
        <WasIt changes={changes} onRowClick={setSelectedChange} />
      </div>

      <RiskInfoButton />

      <button
        className={`scroll-button ${isTableVisible ? 'up' : 'down'}`}
        onClick={isTableVisible ? scrollToTop : scrollToTable}
        aria-label={isTableVisible ? 'Наверх' : 'К таблице'}
      >
        {isTableVisible ? '↑' : '↓'}
      </button>

      {selectedChange && (
        <LineDetailsModal line={selectedChange} onClose={closeModal} />
      )}
    </>
  );
};

export default Comparison;
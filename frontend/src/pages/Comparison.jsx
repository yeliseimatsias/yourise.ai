import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
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
  const { oldFile, newFile, analysisData } = useFiles();

  const [oldLines, setOldLines] = useState([]);
  const [newLines, setNewLines] = useState([]);
  const [changes, setChanges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedLine, setSelectedLine] = useState(null);
  const [hoveredIndex, setHoveredIndex] = useState(null);

  useEffect(() => {
    // Если данных нет (например, обновили страницу F5), возвращаем на загрузку
    if (!analysisData) {
      navigate('/');
      return;
    }

    setLoading(true);
    try {
      const [oldDocJson, newDocJson, analysisJson] = analysisData;

      // Собираем в структуру для парсера
      const result = parseApiResponse({
        old_document: oldDocJson,
        new_document: newDocJson,
        analysis: analysisJson
      });
      
      setOldLines(result.oldLines);
      setNewLines(result.newLines);
      setChanges(result.changes || []);
    } catch (err) {
      console.error("Ошибка парсинга данных:", err);
    } finally {
      setLoading(false);
    }
  }, [analysisData, navigate]);

  const handleLineClick = (line) => {
    if (line.text && line.text.trim()) setSelectedLine(line);
  };

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
              onLineClick={handleLineClick}
              onLineHover={setHoveredIndex}
              hoveredIndex={hoveredIndex}
              loading={loading}
            />
            <DocCard
              title="Новая редакция"
              file={newFile}
              contentLines={newLines}
              onLineClick={handleLineClick}
              onLineHover={setHoveredIndex}
              hoveredIndex={hoveredIndex}
              loading={loading}
            />
          </div>
        </div>
      </section>

      <WasIt changes={changes} />
      <RiskInfoButton />
      
      <LineDetailsModal 
        line={selectedLine} 
        onClose={() => setSelectedLine(null)} 
      />
    </>
  );
};

export default Comparison;
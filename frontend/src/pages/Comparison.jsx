import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useFiles } from '../context/FileContext';
import Header from '../layouts/Header';
import Title from '../components/Title';
import DocCard from '../components/DocCard';
import { MOCK_API_RESPONSE } from '../mocks/mockApiResponse';
import { parseApiResponse } from '../utils/parseApiResponse';
import "../styles/Comparison.css";
import WasIt from '../components/WasIt';
import RiskInfoButton from '../layouts/RiskInfo';
import LineDetailsModal from '../components/LineDetailsModal'; // импортируем новый компонент

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

  useEffect(() => {
    if (!oldFile || !newFile) {
      navigate('/');
    }
  }, [oldFile, newFile, navigate]);

  useEffect(() => {
    if (!oldFile || !newFile) return;

    setLoading({ old: true, new: true });

    // Имитация запроса к API
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

      <WasIt changes={changes} />
      <RiskInfoButton />
      
      <LineDetailsModal line={selectedLine} onClose={closeModal} />
    </>
  );
};

export default Comparison;
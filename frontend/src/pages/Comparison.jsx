import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import * as mammoth from 'mammoth';
import { useFiles } from '../context/FileContext';
import Header from '../layouts/Header';
import Title from '../components/Title';
import DocCard from '../components/DocCard';
import "../styles/Comparison.css";

const mockJson = [
  { line: 1, type: "unchanged" },
  { line: 2, type: "yellow" },
  { line: 3, type: "red" },
  { line: 4, type: "unchanged" },
  { line: 5, type: "green" },
  { line: 6, type: "yellow" },
  { line: 7, type: "red" },
  { line: 8, type: "green" }
];

const readFileLines = async (file, typeResolver = () => 'unchanged') => {
  const arrayBuffer = await file.arrayBuffer();
  const result = await mammoth.extractRawText({ arrayBuffer });
  const text = result.value;

  return text
    .split('\n')
    .map((lineText, index) => ({
      text: lineText,
      originalIndex: index,
      type: typeResolver(index + 1)
    }));
};

const Comparison = () => {
  const navigate = useNavigate();
  const { oldFile, newFile } = useFiles();

  const [oldLines, setOldLines] = useState([]);
  const [newLines, setNewLines] = useState([]);
  const [loading, setLoading] = useState({ old: false, new: false });
  const [error, setError] = useState({ old: '', new: '' });

  useEffect(() => {
    if (!oldFile || !newFile) {
      navigate('/');
    }
  }, [oldFile, newFile, navigate]);

  // Загрузка старого файла
  useEffect(() => {
    if (!oldFile) return;
    setLoading(prev => ({ ...prev, old: true }));
    readFileLines(oldFile, () => 'unchanged')
      .then(lines => setOldLines(lines))
      .catch(() => setError(prev => ({ ...prev, old: 'Ошибка чтения старого файла' })))
      .finally(() => setLoading(prev => ({ ...prev, old: false })));
  }, [oldFile]);

  // Загрузка нового файла
  useEffect(() => {
    if (!newFile) return;
    setLoading(prev => ({ ...prev, new: true }));
    readFileLines(newFile, (lineNumber) => {
      const match = mockJson.find(item => item.line === lineNumber);
      return match ? match.type : 'unchanged';
    })
      .then(lines => setNewLines(lines))
      .catch(() => setError(prev => ({ ...prev, new: 'Ошибка чтения нового файла' })))
      .finally(() => setLoading(prev => ({ ...prev, new: false })));
  }, [newFile]);

  const handleLineClick = (line) => {
    console.log('Клик по строке:', line);
  };

  if (!oldFile || !newFile) return null; // защита, но редирект уже должен сработать

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
              loading={loading.old}
              error={error.old}
            />
            <DocCard
              title="Новая редакция"
              file={newFile}
              contentLines={newLines}
              onLineClick={handleLineClick}
              loading={loading.new}
              error={error.new}
            />
          </div>
        </div>
      </section>
    </>
  );
};

export default Comparison;
import { useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import * as mammoth from 'mammoth';
import Header from '../layouts/Header';
import Title from '../components/Title';
import DocCard from '../components/DocCard';
import "../styles/Comparison.css";

// Мок-данные: line — номер строки в новой редакции (1‑based)
const mockJson = [
  { line: 1, type: "unchanged" }, // Статья 1. Основные положения
  { line: 2, type: "yellow" },    // добавлено "и инноваций"
  { line: 3, type: "red" },       // добавлено "включая иностранных лиц"
  { line: 4, type: "unchanged" }, // Статья 2. Права и обязанности
  { line: 5, type: "green" },     // добавлено "полной и достоверной"
  { line: 6, type: "yellow" },    // добавлено "и предоставлять отчеты"
  { line: 7, type: "red" },       // заменено на "административная ответственность"
  { line: 8, type: "green" }      // новый пункт 4
];

// Универсальная функция чтения файла и обработки строк
const readFileLines = async (file, typeResolver = () => 'unchanged') => {
  const arrayBuffer = await file.arrayBuffer();
  const result = await mammoth.extractRawText({ arrayBuffer });
  const text = result.value;

  return text
    .split('\n')
    .map((lineText, index) => ({
      text: lineText,
      originalIndex: index,
      type: typeResolver(index + 1) // передаём номер строки (1‑based)
    }))
    .filter(line => line.text.trim() !== ''); // сразу отсеиваем пустые
};

const Comparison = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { oldFile, newFile } = location.state || {};

  const [oldLines, setOldLines] = useState([]);
  const [newLines, setNewLines] = useState([]);
  const [loading, setLoading] = useState({ old: false, new: false });
  const [error, setError] = useState({ old: '', new: '' });

  useEffect(() => {
    if (!oldFile || !newFile) {
      navigate('/');
    }
  }, [oldFile, newFile, navigate]);

  // Загрузка старого файла (все строки без подсветки)
  useEffect(() => {
    if (!oldFile) return;
    setLoading(prev => ({ ...prev, old: true }));
    readFileLines(oldFile)
      .then(lines => setOldLines(lines))
      .catch(err => setError(prev => ({ ...prev, old: 'Ошибка чтения старого файла' })))
      .finally(() => setLoading(prev => ({ ...prev, old: false })));
  }, [oldFile]);

  // Загрузка нового файла с применением мок‑разметки
  useEffect(() => {
    if (!newFile) return;
    setLoading(prev => ({ ...prev, new: true }));
    readFileLines(newFile, (lineNumber) => {
      const match = mockJson.find(item => item.line === lineNumber);
      return match ? match.type : 'unchanged';
    })
      .then(lines => setNewLines(lines))
      .catch(err => setError(prev => ({ ...prev, new: 'Ошибка чтения нового файла' })))
      .finally(() => setLoading(prev => ({ ...prev, new: false })));
  }, [newFile]);

  const handleLineClick = (line) => {
    console.log('Клик по строке:', line);
  };

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
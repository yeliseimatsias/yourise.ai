import { useEffect, useState } from 'react';
import Header from "../layouts/Header";
import Title from "../components/Title";
import DocxViewer from "../components/DocxViewer"; // предполагаемый компонент
import Button from '../components/Button';
import '../styles/Export.css';

const Export = () => {
  const [fileBlob, setFileBlob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('docx'); // docx, pdf, txt

  // Загружаем файл отчета при монтировании
  useEffect(() => {
    const loadReport = async () => {
      try {
        const response = await fetch('/report.docx'); // файл лежит в public
        if (!response.ok) throw new Error('Не удалось загрузить отчет');
        const blob = await response.blob();
        setFileBlob(blob);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadReport();
  }, []);

  // Обработчик скачивания
  const handleDownload = () => {
    if (!fileBlob) return;

    let downloadBlob = fileBlob;
    let fileName = `отчет.${selectedFormat}`;

    // Для демонстрации: если выбран PDF или TXT, можно сгенерировать соответствующий файл
    // Пока просто скачиваем исходный DOCX, но с нужным расширением
    if (selectedFormat === 'pdf') {
      // Здесь можно добавить конвертацию docx → pdf (например, через API или библиотеку)
      // Для примера оставим тот же blob, но изменим имя
      downloadBlob = fileBlob;
    } else if (selectedFormat === 'txt') {
      // Можно извлечь текст из docx и сохранить как txt
      // Для простоты используем тот же blob
      downloadBlob = fileBlob;
    }

    const url = URL.createObjectURL(downloadBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <Header />
      <div className="export">
        <div className="export__container container">
          <Title className="export__title">Отчет о сравнении нормативных документов</Title>
          
          {/* Блок отображения отчета */}
          <div className="export__report">
            {loading && <p className="export__loading">Загрузка отчета...</p>}
            {error && <p className="export__error">{error}</p>}
            {fileBlob && <DocxViewer file={fileBlob} />}
          </div>

          {/* Блок выбора формата и скачивания */}
          <div className="export__download">
            <div className="export__format-selector">
              <label htmlFor="format">Выберите формат:</label>
              <select
                id="format"
                value={selectedFormat}
                onChange={(e) => setSelectedFormat(e.target.value)}
              >
                <option value="docx">DOCX</option>
                <option value="pdf">PDF</option>
                <option value="txt">TXT</option>
              </select>
            </div>
            <Button 
                className="export__download-btn"
                variant='blue'
                onClick={handleDownload}
                disabled={!fileBlob}
            >
                Скачать отчет
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Export;
import { useEffect, useState } from 'react';
import { useFiles } from '../context/FileContext';
import Header from "../layouts/Header";
import Title from "../components/Title";
import DocxViewer from "../components/DocxViewer";
import Button from '../components/Button';
import '../styles/Export.css';

const Export = () => {
  const { downloadLinks } = useFiles(); // получаем ссылки из контекста
  const [fileBlob, setFileBlob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('docx');

  useEffect(() => {
    if (!downloadLinks?.docx) {
      setError('Ссылка на отчёт не найдена. Пожалуйста, сначала выполните сравнение документов.');
      setLoading(false);
      return;
    }

    const loadReport = async () => {
      try {
        const response = await fetch(downloadLinks.docx);
        if (!response.ok) throw new Error('Не удалось загрузить отчёт');
        const blob = await response.blob();
        setFileBlob(blob);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadReport();
  }, [downloadLinks]);

  const handleDownload = () => {
    if (!fileBlob) return;

    let downloadBlob = fileBlob;
    let fileName = `отчет.${selectedFormat}`;

    // Если выбран PDF или TXT, пока просто скачиваем DOCX с нужным расширением
    if (selectedFormat === 'pdf') {
      downloadBlob = fileBlob;
    } else if (selectedFormat === 'txt') {
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
          
          <div className="export__report">
            {loading && <p className="export__loading">Загрузка отчета...</p>}
            {error && <p className="export__error">{error}</p>}
            {fileBlob && <DocxViewer file={fileBlob} />}
          </div>

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
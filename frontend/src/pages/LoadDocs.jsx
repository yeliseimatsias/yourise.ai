import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useFiles } from '../context/FileContext';
import "../styles/LoadDocs.css";
import Title from "../components/Title";
import Button from "../components/Button";
import FileUpload from "../components/FileUpload";
import Header from '../layouts/Header';

const LoadDocs = () => {
  const navigate = useNavigate();
  const { setOldFile, setNewFile, setAnalysisData } = useFiles();

  const [oldFileLocal, setOldFileLocal] = useState(null);
  const [newFileLocal, setNewFileLocal] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');

  // Сбрасываем ошибку при изменении файлов
  useEffect(() => {
    setError('');
  }, [oldFileLocal, newFileLocal]);

  const handleCompare = async () => {
    if (!oldFileLocal || !newFileLocal) {
      setError('Пожалуйста, загрузите оба файла');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('old_doc', oldFileLocal);
    formData.append('new_doc', newFileLocal);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/compare/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.log("✅ Ответ от бэкенда:", response.data);

      setOldFile(oldFileLocal);
      setNewFile(newFileLocal);
      setAnalysisData(response.data);
      navigate('/comp');
    } catch (error) {
      console.error("❌ Ошибка загрузки:", error);
      const errorMsg = error.response?.data?.error || "Не удалось связаться с сервером аналитики";
      setError(`Ошибка: ${errorMsg}`);
    } finally {
      setIsUploading(false);
    }
  };

  const bothFilesSelected = oldFileLocal && newFileLocal;
  const buttonVariant = bothFilesSelected ? 'blue' : 'gray';

  return (
    <>
      <Header items={[]} />
      <div className="LoadDocs">
        <div className="LoadDocs__container container">
          <Title className="LoadDocs__title">Загрузите документы для сравнения</Title>
          <div className="LoadDocs__body">
            <FileUpload
              title="Старая редакция"
              file={oldFileLocal}
              onFileSelect={setOldFileLocal}
            />
            <FileUpload
              title="Новая редакция"
              file={newFileLocal}
              onFileSelect={setNewFileLocal}
            />
          </div>
          <div className="LoadDocs__areaforbtn">
            <Button
              onClick={handleCompare}
              variant={buttonVariant}
              disabled={isUploading}
              className="LoadDocs__button"
            >
              {isUploading ? "Обработка и анализ..." : "Сравнить"}
            </Button>
            {error && <div className="LoadDocs__error">{error}</div>}
          </div>
        </div>
      </div>
    </>
  );
};

export default LoadDocs;
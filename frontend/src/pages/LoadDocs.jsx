import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
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

  const handleCompare = async () => {
    if (!oldFileLocal || !newFileLocal) return;

    setIsUploading(true);
    const formData = new FormData();
    // Ключи 'old_doc' и 'new_doc' должны совпадать с ожиданиями Django
    formData.append('old_doc', oldFileLocal);
    formData.append('new_doc', newFileLocal);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/compare/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Сохраняем файлы и результат анализа (те самые 3 JSON)
      setOldFile(oldFileLocal);
      setNewFile(newFileLocal);
      setAnalysisData(response.data); 

      navigate('/comp');
    } catch (error) {
      console.error("Ошибка загрузки:", error);
      alert("Не удалось связаться с сервером аналитики");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <>
      <Header items={[]}/>
      <div className="LoadDocs">
        <div className="LoadDocs__container container">
          <Title className="LoadDocs__title">Загрузите документы для сравнения</Title>
          <div className="LoadDocs__body">
            <FileUpload title="Старая редакция" file={oldFileLocal} onFileSelect={setOldFileLocal} />
            <FileUpload title="Новая редакция" file={newFileLocal} onFileSelect={setNewFileLocal} />
          </div>
          <div className="LoadDocs__areaforbtn">
            {oldFileLocal && newFileLocal && (
              <Button 
                onClick={handleCompare} 
                variant="blue" 
                disabled={isUploading}
              >
                {isUploading ? "Обработка..." : "Сравнить"}
              </Button>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default LoadDocs;
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useFiles } from '../context/FileContext';
import "../styles/LoadDocs.css";
import Title from "../components/Title";
import Button from "../components/Button";
import FileUpload from "../components/FileUpload";
import Header from '../layouts/Header';

const LoadDocs = () => {
  const navigate = useNavigate();
  const { setOldFile, setNewFile } = useFiles();
  const [oldFileLocal, setOldFileLocal] = useState(null);
  const [newFileLocal, setNewFileLocal] = useState(null);

  const handleCompare = () => {
    if (!oldFileLocal || !newFileLocal) return;
    // Сохраняем файлы в контекст
    setOldFile(oldFileLocal);
    setNewFile(newFileLocal);
    navigate('/comp');
  };

  const bothFilesSelected = oldFileLocal && newFileLocal;

  return (
    <>
      <Header items={[]}/>
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
            {bothFilesSelected && (
              <Button onClick={handleCompare} variant="blue" className="LoadDocs__button">
                Сравнить
              </Button>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default LoadDocs;
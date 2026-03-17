import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import "../styles/LoadDocs.css";
import Title from "../components/Title";
import Button from "../components/Button";
import FileUpload from "../components/FileUpload";
import Logo from '../components/Logo';
import Header from '../layouts/Header';

const LoadDocs = () => {
  const navigate = useNavigate();
  const [oldFile, setOldFile] = useState(null);
  const [newFile, setNewFile] = useState(null);

  const handleCompare = () => {
    if (!oldFile || !newFile) return; // дополнительная проверка
    navigate('/comp', { state: { oldFile, newFile } });
  };

  const bothFilesSelected = oldFile && newFile;

  return (
    <>
      <Header items={[]}/>

      <div className="LoadDocs">
        <div className="LoadDocs__container container">
          <Title className="LoadDocs__title">Загрузите документы для сравнения</Title>
          
          <div className="LoadDocs__body">
            <FileUpload 
              title="Старая редакция" 
              file={oldFile}
              onFileSelect={setOldFile}
            />
            <FileUpload 
              title="Новая редакция" 
              file={newFile}
              onFileSelect={setNewFile}
            />
          </div>
          <div className="LoadDocs__areaforbtn">
            {bothFilesSelected && (
              <Button onClick={handleCompare} variant="dark-gray" className="LoadDocs__button">
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
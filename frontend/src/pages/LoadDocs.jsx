import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
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
  const [error, setError] = useState('');

  // Сбрасываем ошибку при изменении файлов
  useEffect(() => {
    setError('');
  }, [oldFileLocal, newFileLocal]);

  const handleCompare = () => {
    if (!oldFileLocal || !newFileLocal) {
      setError('Пожалуйста, загрузите оба файла');
      return;
    }
    setOldFile(oldFileLocal);
    setNewFile(newFileLocal);
    navigate('/comp');
  };

  const bothFilesSelected = oldFileLocal && newFileLocal;
  const buttonVariant = bothFilesSelected ? 'blue' : 'gray';
  // Кнопка всегда активна (disabled убран)
  // const buttonDisabled = !bothFilesSelected; // убираем

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
              // disabled убрали
              className="LoadDocs__button"
            >
              Сравнить
            </Button>
            {error && (
              <div className="LoadDocs__error">{error}</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default LoadDocs;
import { useState, useRef } from 'react';
import '../styles/FileUpload.css';
import Button from './Button';

function FileUpload({ title = "Старая редакция", file, onFileSelect }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'application/pdf' || 
          file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        onFileSelect(file);
      }
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload-container">
      <h1 className="file-upload-title">{title}</h1>
      
      <div
        className={`file-upload-area ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <p className="file-upload-text">перетащите файл или</p>

        <Button variant="blue" className="file-upload-button" onClick={handleButtonClick}>
          выберите
        </Button>
        
        <p className="file-upload-hint">поддерживаются .pdf, .docx</p>
        
        {file && (
          <p className="file-upload-selected">
            Выбран файл: {file.name}
          </p>
        )}
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileSelect}
          className="file-input-hidden"
        />
      </div>
    </div>
  );
}

export default FileUpload;
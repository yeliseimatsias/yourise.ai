import { useEffect, useState } from 'react';
import DocxViewer from './DocxViewer';

const MyComponent = () => {
  const [file, setFile] = useState(null);

  useEffect(() => {
    fetch('/sd.docx')
      .then(res => res.blob())
      .then(blob => {
        // Превращаем Blob в File (если нужно имя)
        const file = new File([blob], 'sd.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
        setFile(file);
      })
      .catch(console.error);
  }, []);

  return (
    <div>
      {file ? <DocxViewer file={file} /> : <p>Загрузка...</p>}
    </div>
  );
};
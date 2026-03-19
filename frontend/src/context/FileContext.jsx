import React, { createContext, useState, useContext } from 'react';

const FileContext = createContext();

export const FileProvider = ({ children }) => {
  const [oldFile, setOldFile] = useState(null);
  const [newFile, setNewFile] = useState(null);
  const [analysisData, setAnalysisData] = useState(null); // Для хранения 3-х JSON

  return (
    <FileContext.Provider value={{ 
      oldFile, setOldFile, 
      newFile, setNewFile, 
      analysisData, setAnalysisData 
    }}>
      {children}
    </FileContext.Provider>
  );
};

export const useFiles = () => useContext(FileContext);
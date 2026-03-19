import React, { createContext, useState, useContext } from 'react';

const FileContext = createContext();

export const FileProvider = ({ children }) => {
  const [oldFile, setOldFile] = useState(null);
  const [newFile, setNewFile] = useState(null);

  return (
    <FileContext.Provider value={{ oldFile, setOldFile, newFile, setNewFile }}>
      {children}
    </FileContext.Provider>
  );
};

export const useFiles = () => useContext(FileContext);
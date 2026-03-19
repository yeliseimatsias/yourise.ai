import api from './instance';

export const docApi = {
  compareDocuments: async (oldFile, newFile) => {
    const formData = new FormData();
    formData.append('old_file', oldFile);
    formData.append('new_file', newFile);

    // Предположим, бэк возвращает массив из 3-х ответов 
    // или у тебя 3 разных эндпоинта. 
    // Если эндпоинт один, но он шлет массив:
    const response = await api.post('/compare/', formData);
    
    // Допустим, response.data выглядит как [oldDocJson, newDocJson, analysisJson]
    const [oldDoc, newDoc, analysis] = response.data;

    // Собираем их в ту структуру, которую ждет наш парсер
    return {
      old_document: oldDoc,
      new_document: newDoc,
      analysis: analysis
    };
  }
};
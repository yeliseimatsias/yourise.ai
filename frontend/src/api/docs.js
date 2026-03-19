import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // Твой URL бэкенда
});

export const docApi = {
  compare: async (oldFile, newFile) => {
    const formData = new FormData();
    // Имена полей 'old_doc' и 'new_doc' должны совпадать с тем, что ждет Django в request.FILES
    formData.append('old_doc', oldFile);
    formData.append('new_doc', newFile);

    const response = await api.post('/compare/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Здесь мы ожидаем массив [oldDocJson, newDocJson, analysisJson]
    return response.data; 
  }
};
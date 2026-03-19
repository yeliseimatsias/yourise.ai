import api from './instance';

export const docApi = {
  // Отправка файлов на сравнение
  compareDocuments: async (oldFile, newFile) => {
    const formData = new FormData();
    formData.append('old_file', oldFile);
    formData.append('new_file', newFile);

    const response = await api.post('/compare/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  
  // Получение истории (если нужно)
  getHistory: () => api.get('/history/').then(res => res.data),
};
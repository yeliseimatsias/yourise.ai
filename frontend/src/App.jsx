import { useState } from 'react'
import { Routes, Route } from 'react-router-dom';

import LoadDocs from './pages/LoadDocs';
import Comparison from './pages/Comparison';
import Export from './pages/Export';

function App() {

  return (
    <Routes>
      <Route path='/' element={<LoadDocs />} />
      <Route path='/comp' element = {<Comparison />} />
      <Route path='/export' element = {<Export />} />
    </Routes>
  )
}

export default App

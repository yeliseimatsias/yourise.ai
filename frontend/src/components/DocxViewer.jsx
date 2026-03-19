import React, { useEffect, useRef } from 'react';
import { renderAsync } from 'docx-preview';

const DocxViewer = ({ file }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (file && containerRef.current) {
      containerRef.current.innerHTML = '';
      renderAsync(file, containerRef.current, null, {
        className: 'docx-viewer',
        inWrapper: false,
        ignoreWidth: false,
        ignoreHeight: true,
        ignoreFonts: false,
        breakPages: true,
        ignoreLastRenderedPageBreak: true,
        renderHeaders: true,
        renderFooters: true,
        renderFootnotes: true,
        renderEndnotes: true,
      }).catch(console.error);
    }
  }, [file]);

  return <div ref={containerRef} className="docx-container" />;
};

export default DocxViewer;
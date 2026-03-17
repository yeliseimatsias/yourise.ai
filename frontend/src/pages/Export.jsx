import { useEffect, useState } from 'react';
import Header from "../layouts/Header"
import Title from "../components/Title"
import DocxViewer from "../components/DocxViewer"

const Export = () => {

    return (
        <>
            <Header />
            <div className="export">
                <div className="export__container container">
                    <Title className="export__title">Отчет о сравнении нормативных документов</Title>
                    <div className="export__text">
                        Дата: 12.03.2026 <br />
                        Документ: Правила внутреннего трудового распорядка (ред.2)
                    </div>
                    
                </div>
            </div>
        </>
    )
}

export default Export
import { useEffect, useState } from 'react';
import Header from "../layouts/Header"
import Title from "../components/Title"

import '../styles/Export.css'

const Export = () => {

    return (
        <>
            <Header />
            <div className="export">
                <div className="export__container container">
                    <Title className="export__title">Отчет о сравнении нормативных документов</Title>
                    <div className="export__text">
                         
                    </div>
                    
                </div>
            </div>
        </>
    )
}

export default Export
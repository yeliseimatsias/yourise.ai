import Header from '../layouts/Header'
import Title from '../components/Title'
import DocCard from '../components/DocCard'


import "../styles/Comparison.css"

const oldArticles = [
  {
    title: "Статья 112.",
    paragraphs: [
      "1. Нормальная продолжительность рабочего времени не может превышать 40 часов в неделю.",
      "2. Для работников в возрасте от четырнадцати до шестнадцати лет устанавливается сокращенная продолжительность рабочего времени: не более 23 часов в неделю.",
      "3. Для работников в возрасте от шестнадцати до восемнадцати лет – не более 35 часов в неделю."
    ]
  },
  {
    title: "Статья 113.",
    paragraphs: [] // пустой массив, чтобы отобразить заголовок без текста
  }
];

const newArticles = [
  {
    title: "Статья 112.",
    paragraphs: [
      "1. Нормальная продолжительность рабочего времени не может превышать 38 часов в неделю.",
      "2. Для работников в возрасте от четырнадцати до шестнадцати лет устанавливается сокращенная продолжительность рабочего времени: не более 24 часов в неделю.",
      "3. Для работников в возрасте от шестнадцати до восемнадцати лет – не более 35 часов в неделю."
    ]
  },
  {
    title: "Статья 113.",
    paragraphs: []
  }
];


const Comparison = () => {
    return (
        <>
            <Header />
            
            <section className="compare_docs">
                <div className="compare_docs__container container">
                    <Title className="compare_docs__title">Сравнение документов</Title>
                    <div className="compare_docs__body">
                        <DocCard title="Старая редакция" articles={oldArticles} />
                        <DocCard title="Новая редакция" articles={newArticles} />
                    </div>
                </div>
            </section>
    
        </>
    )
}

export default Comparison
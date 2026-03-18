import { useNavigate } from 'react-router-dom';
import Button from "../components/Button"
import "../styles/TitlePage.css"

const TitlePage = () => {
    const navigate = useNavigate();

    return (
        <div className="TitlePage">
            <div className="TitlePage__title">
                LexRay AI <br/> Просвечиваем закон <br/>Находим риски
            </div>
            <div className="TitlePage__text text">
                Мы решаем огромную реальную проблему.<br/>
                В Беларуси ежегодно обновляется более 10 000 НПА.<br/>
                Юристы тратят 60-80% времени на ручное сравнение документов. <br/>
                Наш продукт автоматизирует эту работу.
            </div>
            <Button 
                onClick={() => navigate('/load')} 
                variant="blue" 
                className="TitlePage__button"
            >
                Начать работу
            </Button>
        </div>
    )
}

export default TitlePage
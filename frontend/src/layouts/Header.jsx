import Logo from '../components/Logo';
import Navigation from '../components/Navigation';
import '../styles/Header.css';

const Header = ({ items: customItems }) => {
    
    const defaultNavItems = [
        
        { path: '/comp', label: 'Сравнение' },
        { path: '/export', label: 'Экспорт отчета' },
    ];

    const navItems = customItems || defaultNavItems;

    return (
        <header className="header">
            <div className="header__container container">
                <Logo className="header__logo" />
                <Navigation items={navItems} className="header__navigation" />
            </div>
        </header>
    );
};

export default Header;
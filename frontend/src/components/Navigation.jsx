import { NavLink } from 'react-router-dom';

const Navigation = ({ className, items }) => {
  return (
    <nav className={`${className} navigation`}>
      <ul className="navigation__list">
        {items.map((item, index) => (
          <li key={index} className="navigation__item">
            <NavLink
              to={item.path}
              className={({ isActive }) =>
                isActive ? 'navigation__link navigation__link--active' : 'navigation__link'
              }
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navigation;
import '../styles/Logo.css'

import logoimg from '../assets/logo.png'

const Logo = (props) => {
    return (
        <a href="/" className="logo">
            <img className="logo__img" src={logoimg} alt="" />
            <div className="logo__text">LEXRAYAI</div>
        </a>
    )
}

export default Logo
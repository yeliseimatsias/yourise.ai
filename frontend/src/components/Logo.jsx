import '../styles/Logo.css'

const Logo = (props) => {
    return (
        <a href="/" className={`${props.className} logo`}>Yourise.ai</a>
    )
}

export default Logo
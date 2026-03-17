import '../styles/Title.css'

const Title = (props) => {

    return (
        <h1 className={`${props.className} title`}>{props.children}</h1>
    )
}

export default Title
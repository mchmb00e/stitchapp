export default function ContainerAside(props) {

    const { children, width, height, background, shadow, className } = props;

    const ContainerAsideClassName = `${background ? background : ""} ${shadow ? shadow : ""}
     ${className ? className : ""}`;

    const ContainerAsideStyle = {
        width: width || 'auto',
        height: height || 'auto',
    };

    return <div className={ContainerAsideClassName} style={ContainerAsideStyle}>
        { children }
    </div>
}
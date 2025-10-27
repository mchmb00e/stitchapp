export default function Logo(props) {
    const { width = '100px', height, border } = props;

    // Creamos un objeto de estilo para pasar las props
    const logoStyle = {
        width: width,
        height: height || 'auto',
        border: border || '0px solid black'
    };

    return (
        <img 
            src="/Logo.svg"
            alt="Logo de la empresa"
            style={logoStyle}
        />
    );
}
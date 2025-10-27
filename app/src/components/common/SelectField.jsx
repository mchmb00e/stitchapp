// 1. Importa 'Select' de 'react-select' en lugar de usar un <select> nativo
import Select from 'react-select';
import Icon from "@/components/common/Icon";

export default function SelectField(props) {
    // 2. Recibimos las props estándar de react-select:
    // 'value' (el objeto de opción seleccionado)
    // 'onChange' (la función para actualizar el estado)
    // 'placeholder', 'options', 'width'
    const { options, width, value, onChange, placeholder } = props;

    // 3. react-select se estiliza con un objeto 'styles', no con 'style'
    const customStyles = {
        // Esto aplica el 'width' al contenedor principal
        container: (provided) => ({
            ...provided,
            width: width || 'auto',
        }),
    };

    // 4. ¡La Magia! Esta función le dice a react-select CÓMO
    // renderizar la etiqueta de cada opción en la lista.
    const formatOptionLabel = ({ label, icon }) => (
        <div className="d-flex align-items-center gap-2">
            {/* Usamos tu componente Icon tal como querías */}
            <Icon name={icon} size={18} /> 
            <span>{label}</span>
        </div>
    );

    // 5. Renderizamos el componente <Select>
    return (
        <Select
            value={value}
            onChange={onChange}
            options={options}
            styles={customStyles}
            formatOptionLabel={formatOptionLabel} // <-- Aquí aplicamos el formato
            placeholder={placeholder || "Selecciona una opción..."}
            classNamePrefix="react-select" // Prefijo de clase para CSS (opcional)
        />
    );
}
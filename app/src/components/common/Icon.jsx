// 1. Importa TODO el paquete y ponlo en un objeto llamado 'icons'
import * as icons from 'react-bootstrap-icons';

export default function Icon(props) {
  // Asumimos que la prop 'iconName' es un string como "HeartFill" o "Search"
  const { name, size } = props;

  // 2. Accedemos al componente usando el string
  // ¡El alias DEBE empezar con Mayúscula para que React lo reconozca!
  const IconComponent = icons[name];

  // 3. Si el ícono no existe, evitamos un error
  if (!IconComponent) {
    console.warn(`Ícono no encontrado: ${iconName}`);
    return null; // O un ícono por defecto
  }

  // 4. Renderizamos el componente dinámico
  // Pasamos el resto de las props (como size, color)
  return <IconComponent size={size || 20} />;
}
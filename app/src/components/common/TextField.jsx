import styles from './TextField.module.css';

export default function TextField(props) {
    const { width, align, onChange, placeholder } = props;

    const dynamicStyles = {
        width: width || '100%',
        textAlign: align || 'left'
    };

    return (
        <input 
            type="text" 
            className={styles.textField}
            style={dynamicStyles}
            onChange={onChange}
            placeholder={placeholder}
        />
    );
}
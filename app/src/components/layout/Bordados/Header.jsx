import Logo from '@/components/common/Logo';
import TextField from '@/components/common/TextField';
import Button from '@/components/common/Button';
import SelectField from '@/components/common/SelectField';

export default function Header(props) {

    const { height, selectOptions } = props;

    const headerClassName = `bg-light w-100 d-flex justify-content-center align-items-center shadow-md position-fixed z-3`;
    const headerStyle = {
        height: height || "auto",
    };

    
    const handleChange = (e) => console.log(e.target.value);
    const handleSelectChange = (e) => console.log(e.value);

    return <header className={headerClassName} style={headerStyle}>
        <div className="container-lg w-100 h-50 d-flex justify-content-between align-items-center">
            <div style={{height:'100%', width:"33%"}} >
                <Logo height="100%" width="auto" />
            </div>
            <div style={{height:'100%', width:"450px"}} className="d-flex flex-column justify-content-center gap-2">
                <TextField placeholder="Buscar un bordado..." align="center" width="100%"  onChange={e => handleChange(e)}/>
                <div className="d-flex justify-content-between w-100 gap-2">
                    <div className="d-flex w-100">
                        <span className="text-dark" style={{fontSize: "20px", width: "150px"}}>Filtrar por: </span>
                        <SelectField options={selectOptions} placeholder="Orden de búsqueda" width="100%" onChange={(e) => handleSelectChange(e)}/>
                    </div>
                    <Button icon="HeartFill"></Button>
                </div>
            </div>
            <div style={{height:'100%', width:"33%"}} className="d-flex align-items-center justify-content-end">
                <Button icon="PlusCircleFill">Subir bordado</Button>
            </div>
        </div>
    </header>
}
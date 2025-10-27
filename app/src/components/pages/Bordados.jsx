import Header from '@/components/layout/Bordados/Header'
import AsideLeft from '@/components/layout/Bordados/AsideLeft'
//import Aside from '@/components/layout/Bordados/AsideRight'
//import Main from '@/components/layout/Bordados/Main'

export default function Bordados() {

    const selectOptions = [
        {icon: 'SortAlphaDown', label: 'Ascendente', value: 1},
        {icon: 'SortAlphaUp', label: 'Descendente', value: 2},
        {icon: 'CaretUpFill', label: 'Ascendente', value: 3},
        {icon: 'CaretDownFill', label: 'Descendente', value: 4}
    ];


    return <>
        <Header height="200px" selectOptions={selectOptions} />
        <div className="d-flex justify-content-center bg-secondary" style={{position: 'fixed', top: '200px'}}>
            <div className="container-lg d-flex flex-row justify-content-between">
                <AsideLeft className="col-3"/>
                <div className="col-6 bg-primary" style={{height: '300px'}}></div>
                <div className="col-3 bg-dark" style={{height: '300px'}}></div>
            </div>
        </div>
    </>
}
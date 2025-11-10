import Header from '@/components/layout/Bordados/Header'
import Main from '@/components/layout/Bordados/Main'

export default function Bordados() {

    const height = '200px';

    const selectOptions = [
        {icon: 'SortAlphaDown', label: 'Ascendente', value: 1},
        {icon: 'SortAlphaUp', label: 'Descendente', value: 2},
        {icon: 'CaretUpFill', label: 'Ascendente', value: 3},
        {icon: 'CaretDownFill', label: 'Descendente', value: 4}
    ];


    return <>
        <Header height={height} selectOptions={selectOptions} />
        <Main height={height} />
    </>
}
import Filter from '@/components/layout/Bordados/Filter'

export default function Main(props) {
    const { height } = props;

    const baseClassName = `bg-secondary position-fixed z-2 w-100 p-5`;

    const baseStyle = {
        top: height || '0px'
    };

    return <div className={baseClassName} style={baseStyle}>
        <div className="container-lg">
            <Filter />
        </div>
    </div>
}
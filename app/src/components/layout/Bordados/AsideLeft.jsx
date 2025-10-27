import ContainerAside from "@/components/common/ContainerAside"

export default function AsideLeft(props) {

    const { className } = props.className;

    return <ContainerAside className={className ? className : ""}>
        Hola mundo
    </ContainerAside>
}
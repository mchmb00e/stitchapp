import { PlusCircleFill, HeartFill } from "react-bootstrap-icons";
import Icon from "@/components/common/Icon";

export default function Button(props) {
    const { width, height, icon, children, onClick } = props;

    const buttonClassName = `btn btn-primary btn-push text-light d-flex gap-2 align-items-center
    `;

    const buttonStyle = {
        fontSize: "24px",
    };

    return <button type="button" style={buttonStyle} className={buttonClassName} onClick={onClick}>
        <Icon size={20} name={icon} />
        {children}</button>

}
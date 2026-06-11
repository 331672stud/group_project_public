import styles from './Button.module.css'
import {useNavigate} from "react-router-dom";
import {Icon} from "../Icon/Icon.jsx";
import Label from "../Label/Label.jsx";
import {IconComponent} from "../Icon/IconComponent.jsx";

export function Button({status, link, action}) {
    const navigate = useNavigate()
    const handleClick = link ? () => navigate(link) : action ? action : null
    return (
        <button
            onClick={handleClick}
            className={`${styles.button} ${styles[status]}`}>
            <IconComponent Icon={Icon[status]} className={styles.icon}/>
            <Label text={status.charAt(0).toUpperCase() + status.slice(1)} size={'medium'}/>
        </button>
    )
}
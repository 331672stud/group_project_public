import styles from "./IconButton.module.css"
import {Link} from "react-router-dom";
import {IconComponent} from "../IconComponent.jsx"
import {useDraggable} from "@dnd-kit/react";

export function IconLink ({link, Icon, className})
{
    return <>
        <Link to={link} className={`${styles.button} ${styles.bordered} ${className}`}><IconComponent Icon={Icon} className={styles.icon}/></Link>
    </>
}

export function IconButton ({onClick, Icon, className, ...props}) {
    return <div {...props} className={`${styles.button} ${className}` } onClick={onClick}><IconComponent Icon={Icon} className={styles.icon}/></div>
}

export function DraggableIconButton ({id, onClick, Icon, ...props}) {
    const {ref} = useDraggable({id: id})
    return <IconButton {...props} Icon={Icon} onClick={onClick} ref={ref}/>
}
import styles from "./TopBar.module.css"
import {Settings, SquareChartGantt, UserRound, Undo2, BookOpenText} from "lucide-react";
import Label from "../Label/Label.jsx";
import {IconLink} from "../Icon/IconButton/IconButton.jsx";
import {textConvert} from "../../Utility/textConvert.js";
import {IconComponent} from "../Icon/IconComponent.jsx";
import {useContext} from "react";
import {AuthorizationContext} from "../../Utility/AuthorizationContext.jsx";

function TopBar({topic, small}) {
    const {user, setUser} = useContext(AuthorizationContext)
    if(setUser === null)
        return null
    const logout = async () => {
        try {
            await fetch(`${import.meta.env.VITE_BACKEND_URL}logout`, {credentials: 'include'})
            setUser(null)
        } catch (e) {
            console.log(e)
        }
    }
    return <>
        <div className={`${styles.body} ${small ? styles.small : null}`}>
            <div className={styles.bar}>
                <div className={styles.menuButton}>
                    <IconComponent Icon={SquareChartGantt} className={styles.icon} style={{rotate: "180deg"}}/>
                    <Label text={'Menu'} size={'medium'} className={styles.label}/>
                </div>
                <div className={styles.settingsUserGroup}>
                    <Label text={user["first name"] + " " + user["last name"]} size={'small'}/>
                    <IconComponent Icon={UserRound} className={styles.icon}/>
                    <IconComponent Icon={Settings} className={styles.icon}/>
                    <button onClick={logout}>Logout</button>
                </div>
            </div>
            {topic != null ? (<div className={styles.underBar}>
                <IconLink Icon={Undo2} link={small ? `/menu/${topic}` : '/menu'} className={styles.icon}/>
                <Label text={topic} size={'medium'} weight={'bold'}/>
                <IconLink Icon={BookOpenText} link={small ? `/menu/${topic}` : '/menu'} className={styles.icon}/>
            </div>) : (<></>)}
        </div>
    </>
}


export default TopBar
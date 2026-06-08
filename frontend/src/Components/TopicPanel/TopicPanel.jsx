import styles from "./TopicPanel.module.css"
import Label from "../Label/Label.jsx";
import {textConvert} from "../../Utility/textConvert.js";
import {exercises} from "../../Utility/fakeAPI/Exercises.js";
import {BookOpenText, NotebookPen} from "lucide-react";
import {IconLink} from "../Icon/IconButton/IconButton.jsx";

function TopicPanel({topic}) {
    const thisExercises = exercises.filter(e => e.topic === topic)
    return (
        <>
            <div className={styles.component}>
                <div className={styles.header}>
                    <Label className={styles.title} size={"large"} text={textConvert(topic)}/>
                </div>
                <div className={styles.body}>
                    <div className={styles.iconsContainer}>
                            <IconLink link={`/menu/${topic}`} Icon={BookOpenText} className={styles.button}/>
                            <IconLink link={`/menu/${topic}`} Icon={NotebookPen} className={styles.button}/>

                    </div>
                    <div className={styles.progressBarContainer}>
                        {['theory', 'easy', 'medium', 'hard'].map(diff => (
                            <ProgresBar color={diff} exercises={
                                thisExercises.filter(e => e.difficulty === diff)}/>
                        ))}

                    </div>
                </div>
            </div>
        </>
    )
}

function ProgresBar({color, exercises}) {
    const label = color.charAt(0).toUpperCase() + color.slice(1)
    const done = exercises.filter(e => e.status === 'done').length
    const all = exercises.length
    const percentage = 100*done/all
    return (
        <>

            <div className={styles.progressBar}>
                <div className={styles.barTitle}><Label text={label} size={'small'}/></div>
                <div className={styles.barPlusNumGroup}>
                        <div className={styles.barBackground}>
                            <div className={`${styles.barProgres} ${styles[color]}`}
                                 style={{right: 100 - percentage + '%'}}/>
                        </div>
                        <div className={styles.barNum}><Label text={done+'/'+all} size={'small'}/></div>
                </div>


            </div>

        </>
    )
}

export default TopicPanel
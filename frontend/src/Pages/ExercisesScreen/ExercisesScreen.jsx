import {useState, useEffect} from "react";
import ExerciseIcon from "../../Components/ExerciseIcon/ExerciseIcon.jsx";
import {exercises} from "../../Utility/fakeAPI/Exercises.js";
import styles from './ExercisesScreen.module.css'
import Label from "../../Components/Label/Label.jsx";
import {IconComponent} from "../../Components/Icon/IconComponent.jsx"
import {useParams} from "react-router-dom";
import {textConvert} from "../../Utility/textConvert.js";
import {useNavigate} from "react-router-dom"
import TopBar from "../../Components/TopBar/TopBar.jsx";
import {Icon} from "../../Components/Icon/Icon.jsx";

function ExercisesScreen() {
    const [activeExercise, updateActivateExercise] = useState(null)
    const [exerciseList, updateExerciseList] = useState(null)

    useEffect(() => {
        const e = fetch(`${import.meta.env.VITE_BACKEND_URL}tasks`, {credentials: 'include'}).then(res => res.json()).then(data => {
            updateExerciseList(data['tasks'])
        })
    }, []);

    const onUpdateActiveExercise = (e) => {
        updateActivateExercise(e)
    }
    const {topic} = useParams()
    return (<>
        <TopBar topic={topic}/>
        <div className={styles.pageWrapper}>
            <div className={styles.exerciseSections}>
                {['easy', 'medium', 'hard'].map(diff => (
                    <Section key={diff} difficulty={diff} activeExerciseState={ {activeExercise, onUpdateActiveExercise} } exerciseList={exerciseList} />
                ))}
            </div>
            <ExerciseInfo exercise={activeExercise}/>
        </div>
    </>)
}

function Section({ difficulty, activeExerciseState, exerciseList }) {
    const { topic } = useParams();

    return (
        <>
            <Label
                className={styles.sectionLabel}
                text={difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                size={"small"}
            />

            {exerciseList?.length > 0 && (
                <div className={styles.exerciseSection}>
                    {exerciseList
                        .filter(
                            (e) =>
                                e.difficulty === difficulty &&
                                e.topic === topic
                        )
                        .sort((a, b) => a.num - b.num)
                        .map((e) => (
                            <ExerciseIcon
                                key={e.num}
                                exercise={e}
                                activeExerciseState={activeExerciseState}
                            />
                        ))}
                </div>
            )}
        </>
    );
}

function ExerciseInfo({exercise}) {
    return <>
        <div className={styles.exerciseInfoSection}>
            <div className={styles.exerciseInfoBackground}>
                {exercise == null ? (<></>) : (<>
                    <table className={styles.table}>
                        <tbody>
                        {Object.entries(exercise).map(([key, value]) => {
                            key = textConvert(key) + ':'
                            value = value
                            return (
                                <tr key={key} className={styles.tableRow}>
                                    <td className={styles.tableKey}><Label text={key} size={'small'}/></td>
                                    <td className={styles.tableValue}><Label text={value} size={'small'}/></td>
                                </tr>)
                        })}
                        </tbody>
                    </table>
                    <div className={styles.buttons}>
                        {
                            exercise.status === 'new' ? (
                                <Button status={'start'} exercise={exercise}/>
                            ) : exercise.status === 'inProgress' ? (
                                <>
                                    <Button status={'continue'} exercise={exercise}/>
                                    <Button status={'restart'} exercise={exercise}/>
                                </>
                            ) : exercise.status === 'done' ? (
                                <>
                                    <Button status={'view'} exercise={exercise}/>
                                    <Button status={'restart'} exercise={exercise}/>
                                </>
                            ) : (
                                <>
                                </>
                            )
                        }
                    </div>
                </>)}

            </div>
        </div>
    </>
}

function Button({status, exercise}) {
    const navigate = useNavigate()
    const link = `/menu/${exercise.topic}/${exercise.num}`
    return (
        <button
            onClick={() => navigate(link)}
            className={`${styles.button} ${styles[status]}`}>
            <IconComponent Icon={Icon[status]} className={styles.icon}/>
            <Label text={status.charAt(0).toUpperCase() + status.slice(1)} size={'medium'}/>
        </button>
    )
}

export default ExercisesScreen
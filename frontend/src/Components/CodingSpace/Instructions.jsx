import styles from "./CodingSpace.module.css"
import {useContext} from "react";
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import { Button } from "../Button/Button.jsx";
import {bar, panel} from "../../Utility/Enums.js";

export function Instructions() {
    const {task, files, setButtonsPos, setPanelPos, setSubmissionId} = useContext(CodingSpaceContext);
    const save = () => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}tasks/${task.id}/progress`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                status: "inProgress",
                lastViewed: new Date().toISOString(),
                files: files
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
        })
        
    }
    const submit = () => {
        const e = fetch(`${import.meta.env.VITE_BACKEND_URL}tasks/${task.id}/submit`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                files: files,
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            } else {
                setButtonsPos(prev => {return {...prev, [panel.results]: bar.right}})
                setPanelPos(prev => {return {...prev, [bar.right]: panel.results}})
            }
            return response.json()
        })
        .then(content => {
            setSubmissionId(content['submission_id'])
        } )
        
    }
    return <>
        <div className={styles.instructions}>
            <div>
                <h3>Polecenie</h3>
                <p>
                    {task?.description}
                </p>
            </div>
            <div style={{paddingBottom: "30px"}}>
                <Button status={"save"} action={save}/>
                <Button status={"submit"} action={submit}/>
            </div>
            
        </div>
    </>
}
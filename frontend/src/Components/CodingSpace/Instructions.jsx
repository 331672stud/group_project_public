import styles from "./CodingSpace.module.css"
import {useContext} from "react";
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import { Button } from "../Button/Button.jsx";

export function Instructions() {
    const {task, files} = useContext(CodingSpaceContext);
    const save = () => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}tasks/${task.id}/progress`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                status: "inProgress",
                lastViewed: new Date().toLocaleString("pl-PL", {
                        year: "numeric",
                        month: "2-digit",
                        day: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                    }),
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
        })
        
    }
    const submit = () => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}tasks/${task.id}/submit`, {
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
            }
        })
        
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
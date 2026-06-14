import styles from "./CodingSpace.module.css"
import {useContext, useState} from "react";
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import { Button } from "../Button/Button.jsx";
import {bar, panel} from "../../Utility/Enums.js";

export function Instructions() {
    const {task, files, setButtonsPos, setPanelPos, setSubmissionId} = useContext(CodingSpaceContext);
    const [answerResult, setAnswerResult] = useState(null)

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

    const submitAnswer = (answer) => {
        setAnswerResult({status: 'pending'})
        fetch(`${import.meta.env.VITE_BACKEND_URL}tasks/${task.id}/submit_answer`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            credentials: "include",
            body: JSON.stringify({answer})
        })
        .then(r => r.json().then(data => ({ok: r.ok, data})))
        .then(({ok, data}) => {
            if (!ok) {
                const msg = data?.detail || data?.message || 'Błąd wysyłania odpowiedzi'
                setAnswerResult({status: 'error', message: msg})
                return
            }
            const res = data
            if (res.correct) {
                setAnswerResult({status: 'ok', message: 'Poprawna odpowiedź'})
            } else {
                const msg = res.message || 'Niepoprawna odpowiedź'
                setAnswerResult({status: 'error', message: msg})
            }
        })
        .catch(e => setAnswerResult({status: 'error', message: 'Błąd wysyłania odpowiedzi'}))
    }

    return <>
        <div className={styles.instructions}>
                <div>
                    <h3>Polecenie</h3>
                    <p>
                        {task?.description}
                    </p>
                </div>

                <div style={{marginTop: '12px', marginBottom: '16px'}}>
                    <h4>Odpowiedź</h4>
                    <AnswerBox onSubmit={submitAnswer} result={answerResult} />
                </div>

                {task?.answer === undefined || task?.answer === null ? (
                    <div style={{paddingBottom: "30px"}}>
                        <Button status={"save"} action={save}/>
                        <Button status={"submit"} action={submit}/>
                    </div>
                ) : null}
            
        </div>
    </>
}

function AnswerBox({onSubmit, result}){
    const handle = (e) => {
        e.preventDefault();
        const v = e.target.elements['answer'].value
        onSubmit(v)
    }
    const color = result ? (result.status === 'ok' ? 'green' : (result.status === 'pending' ? 'gray' : 'red')) : null
    return (
        <form onSubmit={handle} style={{display:'flex', gap: '8px', flexDirection: 'column', marginTop: '8px'}}>
            <div style={{display:'flex', gap:'8px'}}>
                <input name="answer" placeholder="Wpisz odpowiedź" style={{flex:1, padding:'6px'}} />
                <button type="submit">Wyślij</button>
            </div>
            {result && result.status !== 'pending' ? (
                <div style={{marginTop: '6px', color: color}}>
                    {result.message}
                </div>
            ) : null}
        </form>
    )
}
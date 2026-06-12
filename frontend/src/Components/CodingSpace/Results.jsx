import styles from "./CodingSpace.module.css"
import {useContext, useEffect, useState} from "react";
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import { Button } from "../Button/Button.jsx";
import {bar, panel} from "../../Utility/Enums.js";
import Label from "../Label/Label.jsx";
import { textConvert } from "../../Utility/textConvert.js";

export function Results() {
    const {submissionId} = useContext(CodingSpaceContext);
    const [result, setResult] = useState({})
    useEffect(() => {
        if (submissionId !== null) {
            fetch(`${import.meta.env.VITE_BACKEND_URL}submissions/${submissionId}/result`, {
            credentials: "include",
            })
            .then(response => response.json())
            .then(content => setResult(content))
        }
        
    }, [submissionId])
    
    return <>
        <div className={styles.instructions}>
            <div>
                <h3>Wyniki</h3>
                {result === null ? 'Loading...' : 
                <table>
                        <tbody>
                        {Object.entries(result).map(([key, value]) => {
                            key = textConvert(key) + ':'
                            value = value
                            return (
                                <tr key={key}>
                                    <td><Label text={key} size={'small'}/></td>
                                    <td><Label text={value} size={'small'}/></td>
                                </tr>)
                        })}
                        </tbody>
                    </table>
                }
            </div>
        </div>
    </>
}
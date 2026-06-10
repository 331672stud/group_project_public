import TopicPanel from "../../Components/TopicPanel/TopicPanel.jsx"
import styles from "./TopicsScreen.module.css"
import {exercises} from "../../Utility/fakeAPI/Exercises.js";
import TopBar from "../../Components/TopBar/TopBar.jsx";
import {useState, useEffect} from "react";

function TopicsScreen() {
    const [exerciseList, updateExerciseList] = useState([])
    const [topics, updateTopics] = useState([])
    
    useEffect(() => {
        console.log("log")
        const e = fetch(`${import.meta.env.VITE_BACKEND_URL}tasks`, {credentials: 'include'}).then(res => res.json()).then(data => {
            console.log(data)
            updateTopics([...new Set(data['tasks'].map(e => e.topic))])
        })
    }, []);
    console.log(topics)
    return (
        <>
            <TopBar/>
            <div className={styles.wrapper}>
                {
                    topics.map((e, i) => (
                        <TopicPanel key={i} topic={e}/>
                    ))
                }
            </div>
        </>
    )
}

export default TopicsScreen
import TopicPanel from "../../Components/TopicPanel/TopicPanel.jsx"
import styles from "./TopicsScreen.module.css"
import {exercises} from "../../Utility/fakeAPI/Exercises.js";
import TopBar from "../../Components/TopBar/TopBar.jsx";

function TopicsScreen() {
    const topics = [...new Set(exercises.map(e => e.topic))]
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
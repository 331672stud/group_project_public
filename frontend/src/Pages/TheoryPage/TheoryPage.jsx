import { useParams } from "react-router-dom";
import MarkdownPage from "../../Components/MarkdownPage/MarkdownPage";
import TopBar from "../../Components/TopBar/TopBar";
import styles from "./TheoryPage.module.css"

export default function TheoryPage() {
  const { topic } = useParams();

  const link = topic
    ? "../../Theory/" + encodeURIComponent(topic) + ".md"
    : "../../Theory/404.md"

  return (
    <>
      <TopBar topic={topic} theory/>
      <div className={styles.pageWrapper}>
        <MarkdownPage file={link} />
      </div>
      
    </>
  );
}
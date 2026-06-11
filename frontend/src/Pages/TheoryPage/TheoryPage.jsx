import { useParams } from "react-router-dom";
import MarkdownPage from "../../Components/MarkdownPage/MarkdownPage";
import TopBar from "../../Components/TopBar/TopBar";
import styles from "./TheoryPage.module.css"

export default function TheoryPage() {
  const { topic } = useParams();

  const link = "../../Theory/" + topic + ".md"

  return (
    <>
      <TopBar topic={topic} theory/>
      <div className={styles.pageWrapper}>
        <MarkdownPage
        file={link ?? "../../Theory/404.md"}
        />
      </div>
      
    </>
  );
}
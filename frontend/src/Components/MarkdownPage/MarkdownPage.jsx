import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import styles from "./MarkdownPage.module.css"

export default function MarkdownPage({ file }) {
  const [content, setContent] = useState("");

  useEffect(() => {
    fetch(file)
      .then(res => res.text())
      .then(setContent);
  }, [file]);

  return <div className={styles.markdown}><ReactMarkdown>{content}</ReactMarkdown></div>;
}
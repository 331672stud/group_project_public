import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import styles from "./MarkdownPage.module.css"

export default function MarkdownPage({ file }) {
  const [content, setContent] = useState("");

  useEffect(() => {
    fetch(file)
      .then(async (res) => {
        const text = await res.text();
        const ct = res.headers.get("content-type") || "";

        if (ct.includes("text/html") || text.trim().toLowerCase().startsWith("<!doctype html") || text.includes("<html")) {
          setContent(`# Błąd
Nie znaleziono pliku: ${file}`);
        } else {
          setContent(text);
        }
      })
      .catch(() => setContent(`# Błąd
Nie można wczytać pliku: ${file}`));
  }, [file]);

  return <div className={styles.markdown}><ReactMarkdown>{content}</ReactMarkdown></div>;
}
import styles from "./CodingSpace.module.css"

export function Instructions(title, text) {
    return <>
        <div className={styles.instructions}>
            <h3>{title}</h3>
            <p>
                {text}
            </p>
        </div>
    </>
}
import styles from "./Label.module.css"

function Label({className, text, size, weight, color}) {
    return (
        <>

            <p className={`${styles.label} 
                           ${styles[size]} 
                           ${styles[weight]} 
                           ${styles[color]} 
                           ${className}`}>{text}</p>

        </>
    )
}

export default Label
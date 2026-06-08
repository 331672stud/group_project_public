import Label from "../../Components/Label/Label.jsx";
import styles from "./LoginPage.module.css"
export default function LoginPage() {
    const login = async () => {
        window.location.href = `${import.meta.env.VITE_BACKEND_URL}login`
    }

    return <>
        <div className={styles.wrapper}>
            <Label text={"Learn Safe Coding"} size={'large'} weight={'bold'} />
            <button className={styles.button} onClick={login}>USOS Login</button>
        </div>

    </>
}
import {Navigate, Outlet} from "react-router-dom";
import {useContext, useEffect, useState} from "react";
import {AuthorizationContext} from "../Utility/AuthorizationContext.jsx";

export default function ProtectedLayout() {
    const {user, setUser} = useContext(AuthorizationContext)
    const [loading, setLoading] = useState(true)

    const auth = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}profile`, {credentials: 'include'})
            if (response.ok) {
                const newUser = await response.json()
                setUser(newUser)
            } else {
                setUser(null)
            }
        } catch {
            setUser(null)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        auth()
    }, [])

    if(loading) {
        return <div>Ładowanie...</div>
    }

    if (user === null) {
        console.log(user)
        return <Navigate to={'/login'} replace/>
    }

    return <Outlet/>
}
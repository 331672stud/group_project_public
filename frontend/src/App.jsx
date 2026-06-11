import './App.css'
import './index.css'
import {CodingScreen} from "./Pages/CodingScreen/CodingScreen.jsx";
import {createBrowserRouter, Navigate, RouterProvider} from "react-router-dom";
import TopicsScreen from "./Pages/TopicsScreen/TopicsScreen.jsx";
import ExercisesScreen from "./Pages/ExercisesScreen/ExercisesScreen.jsx";
import {useState} from "react";
import {AuthorizationContext} from "./Utility/AuthorizationContext.jsx";
import Layout from "./Layouts/Layout.jsx";
import ProtectedLayout from "./Layouts/ProtectedLayout.jsx";
import LoginPage from "./Pages/LoginPage/LoginPage.jsx";
import TheoryPage from './Pages/TheoryPage/TheoryPage.jsx';

const router = createBrowserRouter([
    {path: "/", element: <Navigate to={'/menu'} replace/>},
    {
        Component: Layout,
        children: [
            {
                Component: ProtectedLayout,
                children: [
                    {path: "/menu", Component: TopicsScreen},
                    {path: "/ex", Component: ExercisesScreen},
                    {path: "/menu/:topic/:id", Component: CodingScreen},
                    {path: "/menu/:topic", Component: ExercisesScreen},
                    {path: "menu/:topic/theory", Component: TheoryPage}
                ]
            },
            {
                path: '/login',
                Component: LoginPage
            }
        ]
    },
]);

function App() {
    const [user, setUser] = useState(null)
    return <>
        <AuthorizationContext value={{user, setUser}}>
            <RouterProvider router={router}/>
        </AuthorizationContext>
    </>
}


export default App

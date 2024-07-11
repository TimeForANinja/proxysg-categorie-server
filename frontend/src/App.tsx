import React from 'react';
import './App.css';
import {
    createBrowserRouter, Navigate, Link,
    RouterProvider, BrowserRouter
} from "react-router-dom";
import MatchingListPage from "./pages/matching";
import LoginPage from "./pages/login";
import ApiTokenPage from "./pages/api-tokens";
import CategoriesPage from "./pages/categories";
import HistoryPage from "./pages/history";
import ProtectedRoute from "./login-protected";
import HomePage from "./pages/home";
import BaseLayout from "./pages/BaseLayout";

function App() {
    const [loggedIn, setLoggedIn] = React.useState<boolean>(false)
    const [username, setUsername] = React.useState<string>('')

    const router = createBrowserRouter([
        {
            element: <BaseLayout />,
            children: [
                {
                    path: "/apitokens",
                    element: <ApiTokenPage/>,
                },
                {
                    path: "/categories",
                    element: <CategoriesPage/>,
                },
                {
                    path: "/history",
                    element: <HistoryPage/>,
                },
                {
                    path: "/matching",
                    element: <MatchingListPage/>,
                },
            ],
        },

        {
            path: "/login",
            element: <LoginPage setLoggedIn={setLoggedIn} setUsername={setUsername}/>,
        },
        {
            path: "/",
            element: <HomePage username={username} loggedIn={loggedIn} setLoggedIn={setLoggedIn}/>,
        },
    ]);

    React.useEffect(() => {
        // Fetch the user username and token from local storage
        const user = JSON.parse(localStorage.getItem('user') ?? '{}')

        // If the token/username does not exist, mark the user as logged out
        if (!user || !user.token) {
            setLoggedIn(false)
            return
        }

        // If the token exists, verify it with the auth server to see if it is valid
        fetch('http://localhost:3080/verify', {
            method: 'POST',
            headers: {
                'jwt-token': user.token,
            },
        })
            .then((r) => r.json())
            .then((r) => {
                setLoggedIn('success' === r.message)
                setUsername(user.username || '')
            })
    }, [])

    return (
        <RouterProvider router={router}/>
    );
}

export default App;

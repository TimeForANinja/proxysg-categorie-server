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
import HomePage from "./pages/home";
import BaseLayout from "./pages/BaseLayout";
import {checkLogin, readLoginToken} from "./model/loginHandler";
import {OptBoolean} from "./model/OptionalBool";

function App() {


    const [loggedIn, setLoggedIn] = React.useState<OptBoolean>(OptBoolean.Unknown)
    const [username, setUsername] = React.useState<string>('')

    const router = createBrowserRouter([
        {
            element: <BaseLayout username={username} loggedIn={loggedIn} setLoggedIn={setLoggedIn}/>,
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
                {
                    path: "/",
                    element: <HomePage/>,
                },
            ],
        },

        {
            path: "/login",
            element: <LoginPage setLoggedIn={setLoggedIn} setUsername={setUsername}/>,
        }
    ]);

    React.useEffect(() => {
        // Fetch the user username and token from local storage
        const user = readLoginToken();

        // If the token/username does not exist, mark the user as logged out
        if (!user || !user.token) {
            setLoggedIn(OptBoolean.No)
            return
        }

        checkLogin(user.token).then(valid => {
            setLoggedIn(valid ? OptBoolean.Yes : OptBoolean.No)
            setUsername(user.username || '')
        })
    }, [loggedIn])

    return (
        <RouterProvider router={router}/>
    );
}

export default App;

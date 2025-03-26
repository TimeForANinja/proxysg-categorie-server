import React from 'react';
import './App.css';
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import MatchingListPage from "./pages/matching";
import LoginPage from "./pages/login";
import ApiTokenPage from "./pages/api-tokens";
import CategoriesPage from "./pages/categories";
import HistoryPage from "./pages/history";
import HomePage from "./pages/home";
import BaseLayout from "./pages/BaseLayout";
import {RedirectToHome} from "./RedirectToHome";
import {AuthProvider} from "./model/AuthContext";

function App() {
    const router = createBrowserRouter([
        {
            element: <BaseLayout/>,
            children: [
                {
                    path: "/token",
                    element: <ApiTokenPage/>,
                },
                {
                    path: "/category",
                    element: <CategoriesPage/>,
                },
                {
                    path: "/history",
                    element: <HistoryPage/>,
                },
                {
                    path: "/url",
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
            element: <LoginPage/>,
        },

        // Default wildcard route to redirect to "/"
        {
            path: "*",
            element: <RedirectToHome/>,
        },

    ]);

    return (
        <AuthProvider>
            <RouterProvider router={router}/>
        </AuthProvider>
    );
}

export default App;

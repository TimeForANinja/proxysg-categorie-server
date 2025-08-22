import React from 'react';
import './App.css';
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import MatchingListPage from "./components/urls";
import LoginPage from "./components/login";
import ApiTokenPage from "./components/apiTokens";
import CategoriesPage from "./components/categories";
import HistoryPage from "./components/history";
import HomePage from "./components/home";
import UploadPage from "./components/upload";
import SettingsPage from "./components/settings";
import BaseLayout from "./components/shared/BaseLayout";
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
                    path: "/upload",
                    element: <UploadPage/>,
                },
                {
                    path: "/settings",
                    element: <SettingsPage/>,
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

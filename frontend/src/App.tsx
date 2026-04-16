import React from 'react';
import './App.css';
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import MatchingListPage from "./components/urls";
import ApiTokenPage from "./components/apiTokens";
import CategoriesPage from "./components/categories";
import HistoryPage from "./components/history";
import HomePage from "./components/home";
import BaseLayout from "./components/shared/BaseLayout";
import {RedirectToHome} from "./RedirectToHome";
import {BranchProvider} from "./hooks/useBranch";
import {AuthProvider} from "./hooks/useLogin";
import LoginPage from "./components/login";


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
            <BranchProvider>
                <RouterProvider router={router}/>
            </BranchProvider>
        </AuthProvider>
    );
}

export default App;

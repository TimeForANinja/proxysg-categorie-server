import React from 'react';
import { Navigate } from "react-router-dom";

interface Props { children: React.ReactNode | React.ReactNode[] }

export const ProtectedRoute = (props: Props) => {
    const { user } = { user: true };
    if (!user) {
        // user is not authenticated
        return <Navigate to="/login"/>;
    }
    return (
        <>
            {props.children}
        </>
    );
};

export default ProtectedRoute;

import React from 'react';
import {Outlet, useNavigate} from "react-router-dom";
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box,
} from '@mui/material';
import BranchSelector from './BranchSelector';
import {OptBoolean} from "../../types/OptionalBool";
import {useAuth} from "../../hooks/useLogin";

const BaseLayout = () => {
    const authMgmt = useAuth();
    const navigate= useNavigate();

    React.useEffect(() => {
        if (authMgmt.loggedIn === OptBoolean.No) {
            // if we are not logged in, then enforce login
            navigate('/login');
        }
        // if loggedIn is unknown -> wait for login check
        // if loggedIn is true -> do nothing and stay on this page
    }, [authMgmt, navigate])

    return (
        <>
            <AppBar position="static">
                <Toolbar>
                    { /* Logo to the left */ }
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        sx={{ display: { xs: 'none', sm: 'block' }, cursor: 'pointer' }}
                        onClick={() => navigate("/")}
                    >
                        CatTracker
                    </Typography>

                    { /* Center Buttons, surrounded by flewGrow to center */ }
                    <Box sx={{ flexGrow: 1 }} />
                    <Button color="inherit" onClick={() => navigate("/url")}>URLs</Button>
                    <Button color="inherit" onClick={() => navigate("/token")}>Api Tokens</Button>
                    <Button color="inherit" onClick={() => navigate("/category")}>Categories</Button>
                    <Button color="inherit" onClick={() => navigate("/history")}>History</Button>
                    <Box sx={{ flexGrow: 1 }} />

                    { /* Branch Selector to the right */ }
                    <BranchSelector />
                </Toolbar>
            </AppBar>

            <Outlet/>
        </>
    );
}

export default BaseLayout;

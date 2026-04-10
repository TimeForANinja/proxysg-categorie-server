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

const BaseLayout = () => {
    const navigate= useNavigate();

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

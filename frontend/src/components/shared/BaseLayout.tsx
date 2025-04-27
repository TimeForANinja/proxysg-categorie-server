import React, {useRef} from 'react';
import {Outlet, useNavigate} from "react-router-dom";
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    IconButton,
    Box,
    Badge,
    Menu,
    MenuItem,
} from '@mui/material';
import AccountCircle from '@mui/icons-material/AccountCircle';
import NotificationsIcon from '@mui/icons-material/Notifications';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

import {OptBoolean} from "../../model/types/OptionalBool";
import {useAuth} from "../../model/AuthContext";

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

    // track the state of the user meu
    const [isMenuOpen, setMenuOpen] = React.useState<boolean>(false);
    const menuRef = useRef(null);

    return (
        <>
            <AppBar position="static">
                <Toolbar>
                    { /* Logo to the left */ }
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        sx={{ display: { xs: 'none', sm: 'block' } }}
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

                    { /* Notification and User Icon to the right */ }
                    <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
                        <IconButton
                            size="large"
                            aria-label="show 17 new notifications"
                            color="inherit"
                        >
                            <Badge badgeContent={17} color="error">
                                <NotificationsIcon />
                            </Badge>
                        </IconButton>
                        <IconButton
                            size="large"
                            aria-label="upload files or text"
                            color="inherit"
                            onClick={() => navigate("/upload")}
                        >
                            <CloudUploadIcon />
                        </IconButton>
                        <IconButton ref={menuRef}
                            size="large"
                            edge="end"
                            aria-label="account of current user"
                            aria-controls='primary-search-account-menu'
                            aria-haspopup="true"
                            onClick={() => setMenuOpen(true)}
                            color="inherit"
                        >
                            <AccountCircle />
                        </IconButton>
                    </Box>
                </Toolbar>
            </AppBar>

            { /* User Menu */ }
            <Menu
                anchorEl={menuRef.current}
                anchorOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                }}
                id='primary-search-account-menu'
                keepMounted
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                }}
                open={isMenuOpen}
                onClose={() => setMenuOpen(false)}
            >
                <MenuItem>Signed in as: {authMgmt.username}</MenuItem>
                <MenuItem>Profile</MenuItem>
                <MenuItem onClick={() => authMgmt.logout()}>Logout</MenuItem>
            </Menu>

            <Outlet/>
        </>
    );
}

export default BaseLayout;

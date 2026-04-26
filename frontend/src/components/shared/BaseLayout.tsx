import React from 'react';
import {Outlet, useNavigate} from "react-router-dom";
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box,
    IconButton,
    Menu,
    MenuItem,
} from '@mui/material';
import BranchSelector from './BranchSelector';
import {OptBoolean} from "../../types/OptionalBool";
import {useAuth} from "../../hooks/useLogin";
import {AccountCircle} from "@mui/icons-material";


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

    const [isMenuOpen, setMenuOpen] = React.useState<boolean>(false);
    const menuRef = React.useRef<HTMLButtonElement | null>(null);

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
                        onClick={() => navigate("/test")}
                    >
                        CatTracker
                    </Typography>

                    { /* Center Buttons, surrounded by flexGrow to center */ }
                    <Box sx={{ flexGrow: 1 }} />
                    <Button color="inherit" onClick={() => navigate("/test")}>Test</Button>
                    <Button color="inherit" onClick={() => navigate("/url")}>URLs</Button>
                    <Button color="inherit" onClick={() => navigate("/token")}>Api Tokens</Button>
                    <Button color="inherit" onClick={() => navigate("/category")}>Categories</Button>
                    <Button color="inherit" onClick={() => navigate("/history")}>History</Button>
                    <Box sx={{ flexGrow: 1 }} />

                    { /* Branch Selector and User Icon to the right */ }
                    <BranchSelector />
                    <IconButton
                        ref={menuRef}
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
                </Toolbar>
            </AppBar>

            { /* User Menu */ }
            <Menu
                anchorEl={menuRef.current}
                anchorOrigin={{
                    vertical: 'bottom',
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
                <MenuItem disabled>Signed in as: {authMgmt.username}</MenuItem>
                <MenuItem onClick={() => { setMenuOpen(false); navigate("/settings"); }}>Settings</MenuItem>
                <MenuItem onClick={() => { setMenuOpen(false); authMgmt.logout(); }}>Logout</MenuItem>
            </Menu>

            { /* Outlet for the main content */}
            <Outlet/>
        </>
    );
}

export default BaseLayout;

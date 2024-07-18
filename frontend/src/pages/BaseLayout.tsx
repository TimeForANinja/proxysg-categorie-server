import React, {useEffect, useRef} from 'react';
import {Outlet, useNavigate} from "react-router-dom";
import {removeLoginToken} from "../model/loginHandler";
import {OptBoolean} from "../model/OptionalBool";

import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Box from '@mui/material/Box';
import Badge from '@mui/material/Badge';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

import AccountCircle from '@mui/icons-material/AccountCircle';
import NotificationsIcon from '@mui/icons-material/Notifications';


interface Props {
    username: string,
    loggedIn: OptBoolean,
    setLoggedIn: React.Dispatch<React.SetStateAction<OptBoolean>>
}

const BaseLayout = (props: Props) => {
    const {loggedIn, username, setLoggedIn} = props
    const navigate= useNavigate();

    useEffect(() => {
        if (loggedIn === OptBoolean.Unknown) {
            // Wait for Login Check
            return;
        } else if (loggedIn === OptBoolean.No) {
            // if we are not logged, in then enforce login
            navigate('/login');
        }
    }, [loggedIn, navigate])

    const doLogout = () => {
        removeLoginToken();
        props.setLoggedIn(OptBoolean.No)
    }


    const [isMenuOpen, setMenuOpen] = React.useState<boolean>(false);
    const menuRef = useRef(null);
    return (
        <>
            <AppBar position="static">
                <Toolbar>
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        sx={{ display: { xs: 'none', sm: 'block' } }}
                        onClick={() => navigate("/")}
                    >
                        CatTracker
                    </Typography>

                    <Box sx={{ flexGrow: 1 }} />
                    <Button color="inherit" onClick={() => navigate("/apitokens")}>Api Tokens</Button>
                    <Button color="inherit" onClick={() => navigate("/categories")}>Categories</Button>
                    <Button color="inherit" onClick={() => navigate("/history")}>History</Button>
                    <Button color="inherit" onClick={() => navigate("/matching")}>Matching</Button>
                    <Box sx={{ flexGrow: 1 }} />

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
                <MenuItem>Signed in as: {username}</MenuItem>
                <MenuItem>Profile</MenuItem>
                <MenuItem onClick={doLogout}>Logout</MenuItem>
            </Menu>

            <Outlet/>
        </>
    );
}

export default BaseLayout;

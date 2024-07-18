import React, {useEffect} from 'react';
import {Link, Outlet, useNavigate} from "react-router-dom";
import './BaseLayout.css';

interface Props {
    username: string,
    loggedIn: boolean,
    setLoggedIn: React.Dispatch<React.SetStateAction<boolean>>
}

const BaseLayout = (props: Props) => {
    const {loggedIn, username} = props
    const navigate = useNavigate()

    useEffect(() => {
        // make sure we are logged in, if not prompt user for a login
        if (!loggedIn) {
            navigate('/login');
        }
    }, [loggedIn, navigate])

    const onLogoutButtonClick = () => {
        localStorage.removeItem('user')
        props.setLoggedIn(false)
    }

    return (
        <>
            <header className="header-navbar">
                <nav>
                    <ul>
                        <li><Link to="/">Home</Link></li>
                        <li><Link to="/apitokens">Api Tokens</Link></li>
                        <li><Link to="/categories">Categories</Link></li>
                        <li><Link to="/history">History</Link></li>
                        <li><Link to="/matching">Matching</Link></li>
                        <li>
                            <div className={'buttonContainer'}>
                                <input
                                    className={'inputButton'}
                                    type="button"
                                    onClick={onLogoutButtonClick}
                                    value={'Log out'}
                                />
                                <div>Your username is {username}</div>
                            </div>
                        </li>
                    </ul>
                </nav>
            </header>

            <Outlet/>
        </>
    );
}

export default BaseLayout;

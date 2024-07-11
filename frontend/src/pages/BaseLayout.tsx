import React from 'react';
import {Link, Outlet} from "react-router-dom";
import './BaseLayout.css';

function BaseLayout() {
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
                    </ul>
                </nav>
            </header>

            <Outlet/>
        </>
    );
}

export default BaseLayout;

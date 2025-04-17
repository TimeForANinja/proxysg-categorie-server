import React from 'react';
import './login.css';
import {useNavigate} from 'react-router-dom'
import {OptBoolean} from "../model/types/OptionalBool";
import {useAuth} from "../model/AuthContext";

function LoginPage() {
    const authMgmt = useAuth();
    const navigate= useNavigate();

    React.useEffect(() => {
        if (authMgmt.loggedIn === OptBoolean.Yes) {
            // if we are logged in, we want to bypass the login page
            navigate('/');
        }
        // if loggedIn is unknown -> wait for login check
        // if loggedIn is false -> do nothing and stay on this page
    }, [authMgmt, navigate])

    const [usernameField, setUsernameField] = React.useState<string>('')
    const [passwordField, setPasswordField] = React.useState<string>('')
    const [usernameError, setUsernameError] = React.useState<string>('')
    const [passwordError, setPasswordError] = React.useState<string>('')

    const onSendLogin = () => {
        // Set initial error values to empty
        setUsernameError('')
        setPasswordError('')

        // Validate Data
        // Check if the user has entered both fields correctly
        if ('' === usernameField) {
            setUsernameError('Please enter your username')
            return
        }
        if (!/^[a-zA-Z0-9_-]+$/.test(usernameField)) {
            setUsernameError('Please enter a valid username')
            return
        }
        if ('' === usernameField) {
            setPasswordError('Please enter a password')
            return
        }
        if (usernameField.length < 4) {
            setPasswordError('The password must be 4 characters or longer')
            return
        }

        // Authentication call
        authMgmt.login(usernameField, passwordField).then(() => {
            navigate('/')
        }).catch((err) => {
            setUsernameError(err.message)
        });
    }

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            onSendLogin();
        }
    }

    return (
        <div className={'mainContainer'}>
            <div className={'titleContainer'}>
                <div>Login</div>
            </div>
            <br/>
            <div className={'inputContainer'}>
                <input
                    value={usernameField}
                    placeholder="Enter your username here"
                    onChange={(ev) => setUsernameField(ev.target.value)}
                    onKeyDown={handleKeyDown}
                    className={'inputBox'}
                />
                <label className="errorLabel">{usernameError}</label>
            </div>
            <br/>
            <div className={'inputContainer'}>
                <input
                    type="password"
                    value={passwordField}
                    placeholder="Enter your password here"
                    onChange={(ev) => setPasswordField(ev.target.value)}
                    onKeyDown={handleKeyDown}
                    className={'inputBox'}
                />
                <label className="errorLabel">{passwordError}</label>
            </div>
            <br/>
            <div className={'inputContainer'}>
                <input className={'inputButton'} type="button" onClick={onSendLogin} value={'Log in'}/>
            </div>
        </div>
    );
}

export default LoginPage;

import React from 'react';
import './login.css';
import {useNavigate} from 'react-router-dom'
import {OptBoolean} from "../model/OptionalBool";
import {doLogin} from "../api/auth";
import {saveLoginToken} from "../model/loginHandler";

interface Props {
    setUsername: React.Dispatch<React.SetStateAction<string>>,
    setLoggedIn: React.Dispatch<React.SetStateAction<OptBoolean>>
}

function LoginPage(props: Props) {
    const [usernameField, setUsernameField] = React.useState<string>('')
    const [passwordField, setPasswordField] = React.useState<string>('')
    const [usernameError, setUsernameError] = React.useState<string>('')
    const [passwordError, setPasswordError] = React.useState<string>('')

    const navigate = useNavigate()

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
        doLogin(usernameField, passwordField).then((user) => {
            saveLoginToken(user)
            props.setLoggedIn(OptBoolean.Yes)
            props.setUsername(user.username)
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

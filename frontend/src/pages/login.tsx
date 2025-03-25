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
    const [username, setUsername] = React.useState<string>('')
    const [password, setPassword] = React.useState<string>('')
    const [usernameError, setUsernameError] = React.useState<string>('')
    const [passwordError, setPasswordError] = React.useState<string>('')

    const navigate = useNavigate()

    const onSendLogin = () => {
        // Set initial error values to empty
        setUsernameError('')
        setPasswordError('')

        // Validate Data
        // Check if the user has entered both fields correctly
        if ('' === username) {
            setUsernameError('Please enter your username')
            return
        }
        if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
            setUsernameError('Please enter a valid username')
            return
        }
        if ('' === password) {
            setPasswordError('Please enter a password')
            return
        }
        if (password.length < 4) {
            setPasswordError('The password must be 4 characters or longer')
            return
        }

        // Authentication call
        doLogin(username, password).then((user) => {
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
                    value={username}
                    placeholder="Enter your username here"
                    onChange={(ev) => setUsername(ev.target.value)}
                    onKeyDown={handleKeyDown}
                    className={'inputBox'}
                />
                <label className="errorLabel">{usernameError}</label>
            </div>
            <br/>
            <div className={'inputContainer'}>
                <input
                    type="password"
                    value={password}
                    placeholder="Enter your password here"
                    onChange={(ev) => setPassword(ev.target.value)}
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

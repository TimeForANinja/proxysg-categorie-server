import React from 'react';
import './login.css';
import {useNavigate} from 'react-router-dom'

interface Props {
    setUsername: React.Dispatch<React.SetStateAction<string>>,
    setLoggedIn: React.Dispatch<React.SetStateAction<boolean>>
}

function LoginPage(props: Props) {
    const [username, setUsername] = React.useState<string>('')
    const [password, setPassword] = React.useState<string>('')
    const [usernameError, setUsernameError] = React.useState<string>('')
    const [passwordError, setPasswordError] = React.useState<string>('')

    const navigate = useNavigate()

    const onButtonClick = () => {
        // Validate Data
        {
            // Set initial error values to empty
            setUsernameError('')
            setPasswordError('')

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
        }

        // Authentication calls
        {
            // Check if username has an account associated with it
            checkAccountExists((accountExists: boolean) => {
                // If yes, log in
                if (accountExists) logIn()
                // Else, ask user if they want to create a new account and if yes, then log in
                else if (
                    window.confirm(
                        'An account does not exist with this username: ' +
                        username +
                        '. Do you want to create a new account?',
                    )
                ) {
                    logIn()
                }
            })
        }
    }

    // Call the server API to check if the given username ID already exists
    const checkAccountExists = (callback: (accountExists: boolean) => void) => {
        fetch('http://localhost:3080/check-account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({username}),
        })
            .then((r) => r.json())
            .then((r) => {
                callback(r?.userExists)
            })
    }

    // Log in a user using username and password
    const logIn = () => {
        fetch('http://localhost:3080/auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({username, password}),
        })
            .then((r) => r.json())
            .then((r) => {
                if ('success' === r.message) {
                    localStorage.setItem('user', JSON.stringify({username, token: r.token}))
                    props.setLoggedIn(true)
                    props.setUsername(username)
                    navigate('/')
                } else {
                    window.alert('Wrong username or password')
                }
            })
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
                    className={'inputBox'}
                />
                <label className="errorLabel">{passwordError}</label>
            </div>
            <br/>
            <div className={'inputContainer'}>
                <input className={'inputButton'} type="button" onClick={onButtonClick} value={'Log in'}/>
            </div>
        </div>
    );
}

export default LoginPage;

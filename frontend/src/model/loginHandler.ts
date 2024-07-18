export interface IUser {
    username: string;
    token: string;
}

export const readLoginToken = (): IUser => {
    return JSON.parse(localStorage.getItem('user') ?? '{}');
}

export const checkLogin = (userToken: string): Promise<boolean> => new Promise((resolve) => {
    // If the token exists, verify it with the auth server to see if it is valid
    fetch('http://localhost:3080/verify', {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
        },
    })
        .then((r) => r.json())
        .then((r) => {
            if ('success' === r.message) resolve(true);
            else resolve(false);
        }).catch(() => resolve(false))
});

export const removeLoginToken = () => {
    localStorage.removeItem('user')
}

// Log in a user using username and password
export const doLogin = (username: string, password: string): Promise<IUser> => new Promise<IUser>((resolve, reject) => {
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
                resolve({
                    username,
                    token: r.token,
                })
            } else {
                reject(new Error('Invalid username or password'));
            }
        }).catch(reject);
});

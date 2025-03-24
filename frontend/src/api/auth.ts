import {IUser} from "../model/loginHandler";

export const checkLogin = async (userToken: string): Promise<boolean> => new Promise((resolve, reject) => {
    fetch('/api/auth/verify', {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
        },
    })
    .then((r) => r.json())
    .then((r) => {
        if ('success' === r.status) resolve(true);
        else resolve(false);
    })
    .catch(() => resolve(false))
});

export const doLogin = async (username: string, password: string): Promise<IUser> => new Promise<IUser>((resolve, reject) => {
    fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username, password}),
    })
    .then((r) => r.json())
    .then((r) => {
        if ('success' === r.status) {
            resolve({
                username,
                token: r.token,
            })
        } else {
            reject(new Error('Invalid username or password'));
        }
    })
    .catch(reject);
});


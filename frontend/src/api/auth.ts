import {IUser} from "../model/loginHandler";

export const checkLogin = async (userToken: string): Promise<boolean> => {
    const response = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
        },
    });

    if (!response.ok) {
        return false;
    }

    const data = await response.json();

    return data.status === "success";
};

export const doLogin = async (username: string, password: string): Promise<IUser> => {
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username, password}),
    })

    if (!response.ok) {
        throw new Error(`Failed to login`);
    }

    const data = await response.json();


    if (data.status === "failed") {
        throw new Error('Invalid username or password');
    }

    return {
        username,
        token: data.token,
    }
}


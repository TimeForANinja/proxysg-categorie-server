import {IUser} from "../types/auth";


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
        const data = await response.json().catch(() => ({}));
        if (data.status === "failed") {
            throw new Error('Invalid username or password');
        }
        throw new Error(`Failed to login`);
    }

    const data = await response.json();

    return {
        username,
        token: data.data.token,
    }
}

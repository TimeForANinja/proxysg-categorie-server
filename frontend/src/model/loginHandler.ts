export interface IUser {
    username: string;
    token: string;
}

const LOCAL_STORAGE_KEY = 'app_user';

export const readLoginToken = (): IUser => {
    return JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) ?? '{}');
}

export const removeLoginToken = () => {
    localStorage.removeItem(LOCAL_STORAGE_KEY)
}

export const saveLoginToken = (user: IUser) => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(user));
}

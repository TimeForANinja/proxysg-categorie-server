export interface IMutableApiToken {
    description: string;
}

export interface IApiToken extends IMutableApiToken {
    id: string;
    token: string;
    categories: string[];
    last_use: number;
}

const TIME_SECONDS = 1000;

export const parseLastUsed = (last_use: number): string => {
    if (last_use === 0) {
        return 'never';
    } else {
        return new Date(last_use * TIME_SECONDS).toLocaleString();
    }
}

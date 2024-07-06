
export interface IApiToken {
    id: number;
    token: string;
    categories: number[];
}


export const getAPITokens = async (): Promise<IApiToken[]> => {
    const response = await fetch('http://127.0.0.1:3080/api/api-tokens');
    const data = await response.json();
    return data.data;
}

export interface IApiToken {
    id: number;
    token: string;
    description: string;
    categories: number[];
    lastUse: string;
}


export const getAPITokens = async (): Promise<IApiToken[]> => {
    const response = await fetch('http://127.0.0.1:3080/api/api-tokens');
    const data = await response.json();
    return data.data;
}

export const updateToken = async (updatedToken: IApiToken): Promise<IApiToken> => {
    const response = await fetch(`http://127.0.0.1:3080/api/api-tokens/${updatedToken.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedToken),
    });

    if (!response.ok) {
        throw new Error(`Failed to update token with id: ${updatedToken.id}`);
    }

    const data = await response.json();
    return data.data;
};

export const createToken = async (partialToken: IApiToken): Promise<IApiToken> => {
    const response = await fetch(`http://127.0.0.1:3080/api/api-tokens`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(partialToken),
    });

    if (!response.ok) {
        throw new Error(`Failed to create token.`);
    }

    const data = await response.json();
    return data.data;
};

export const rotateToken = async (token: IApiToken): Promise<IApiToken> => {
    const response = await fetch(`http://127.0.0.1:3080/api/api-tokens/${token.id}/rotate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to rotate token with id: ${token.id}`);
    }

    const data = await response.json();
    return data.data;
};

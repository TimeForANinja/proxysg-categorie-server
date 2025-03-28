export interface IMutableApiToken {
    description: string;
}

export interface IApiToken extends IMutableApiToken {
    id: number;
    token: string;
    categories: number[];
    last_use: number;
}


export const getAPITokens = async (userToken: string): Promise<IApiToken[]> => {
    const response = await fetch('/api/token', {
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        throw new Error(`Failed to get tokens`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const updateToken = async (userToken: string, id: Number, updatedToken: IMutableApiToken): Promise<IApiToken> => {
    const response = await fetch(`/api/token/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
        body: JSON.stringify(updatedToken),
    });

    if (!response.ok) {
        throw new Error(`Failed to update token with id: ${id}`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
};

export const createToken = async (userToken: string, partialToken: IMutableApiToken): Promise<IApiToken> => {
    const response = await fetch(`/api/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
        body: JSON.stringify(partialToken),
    });

    if (!response.ok) {
        throw new Error(`Failed to create token.`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
};

export const rotateToken = async (userToken: string, id: Number): Promise<IApiToken> => {
    const response = await fetch(`/api/token/${id}/roll`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to rotate token with id: ${id}`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
};

export const deleteToken = async (userToken: string, id: number): Promise<void> => {
    const response = await fetch(`/api/token/${id}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        throw new Error(`Failed to delete category.`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const addTokenCategory = async (userToken: string, id: number, categoryId: number): Promise<void> => {
    const response = await fetch(`/api/token/${id}/category/${categoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to add category ${categoryId} to token with id: ${id}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const deleteTokenCategory = async (userToken: string, id: number, categoryId: number): Promise<void> => {
    const response = await fetch(`/api/token/${id}/category/${categoryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to remove category ${categoryId} from token with id: ${id}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const setTokenCategory = async (userToken: string, id: number, categories: number[]): Promise<number[]> => {
    const response = await fetch(`/api/token/${id}/category`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
        body: JSON.stringify({ categories }),
    });

    if (!response.ok) {
        throw new Error(`Failed to set categories ${categories.join(',')} for token with id: ${id}`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

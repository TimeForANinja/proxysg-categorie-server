export interface IMutableApiToken {
    description: string;
}

export interface IApiToken extends IMutableApiToken {
    id: number;
    token: string;
    categories: number[];
    last_use: number;
}


export const getAPITokens = async (): Promise<IApiToken[]> => {
    const response = await fetch('/api/api-tokens');
    const data = await response.json();
    return data.data;
}

export const updateToken = async (id: Number, updatedToken: IMutableApiToken): Promise<IApiToken> => {
    const response = await fetch(`/api/api-tokens/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedToken),
    });

    if (!response.ok) {
        throw new Error(`Failed to update token with id: ${id}`);
    }

    const data = await response.json();
    return data.data;
};

export const createToken = async (partialToken: IMutableApiToken): Promise<IApiToken> => {
    const response = await fetch(`/api/api-tokens`, {
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

export const rotateToken = async (id: Number): Promise<IApiToken> => {
    const response = await fetch(`/api/api-tokens/${id}/roll`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to rotate token with id: ${id}`);
    }

    const data = await response.json();
    return data.data;
};

export const deleteToken = async (id: number): Promise<void> => {
    const response = await fetch(`/api/api-tokens/${id}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Failed to delete category.`);
    }
}

export const addTokenCategory = async (id: number, categoryId: number): Promise<void> => {
    const response = await fetch(`/api/api-tokens/${id}/category/${categoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to add category ${categoryId} to token with id: ${id}`);
    }
}

export const deleteTokenCategory = async (id: number, categoryId: number): Promise<void> => {
    const response = await fetch(`/api/api-tokens/${id}/category/${categoryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to remove category ${categoryId} from token with id: ${id}`);
    }
}

export const setTokenCategory = async (id: number, categories: number[]): Promise<number[]> => {
    const response = await fetch(`/api/api-tokens/${id}/categories`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ categories }),
    });

    if (!response.ok) {
        throw new Error(`Failed to set categories ${categories.join(',')} for token with id: ${id}`);
    }

    const data = await response.json();
    return data.data;
}

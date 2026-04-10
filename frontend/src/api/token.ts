import {IApiToken, IMutableApiToken} from "../model/types/apiToken";

const getBaseUrl = (branch: string) => `/api/branch/${branch}/token`;

export const getAPITokens = async (branch: string): Promise<IApiToken[]> => {
    const response = await fetch(getBaseUrl(branch));

    if (!response.ok) {
        throw new Error(`Failed to get tokens`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const updateToken = async (branch: string, id: string, updatedToken: IMutableApiToken): Promise<IApiToken> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
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

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
};

export const createToken = async (branch: string, partialToken: IMutableApiToken): Promise<IApiToken> => {
    const response = await fetch(getBaseUrl(branch), {
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

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
};

export const rotateToken = async (branch: string, id: string): Promise<IApiToken> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/roll`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
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

export const deleteToken = async (branch: string, id: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Failed to delete category.`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const addTokenCategory = async (branch: string, id: string, categoryId: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category/${categoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
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

export const deleteTokenCategory = async (branch: string, id: string, categoryId: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category/${categoryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
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

export const setTokenCategory = async (branch: string, id: string, categories: string[]): Promise<string[]> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category`, {
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

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

import {IApiToken, IMutableApiToken} from "../types/apiToken";

const getBaseUrl = (branch: string) => `/api/branch/${branch}/token`;

export const getTokens = async (branch: string): Promise<IApiToken[]> => {
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
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            category: categoryId
        }),
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

import {IApiToken, IApiTokenInput, IApiTokenOutput, IListTokenOutput, IRestTokenDetail} from "../types/apiToken";
import {GenericOutput} from "../types/api";

const getBaseUrl = (branch: string) => `/api/branch/${branch}/token`;

export const getTokens = async (userToken: string, branch: string): Promise<IRestTokenDetail[]> => {
    const response = await fetch(getBaseUrl(branch), {
        headers: { 'jwt-token': userToken },
    });
    const data: IListTokenOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get tokens`);
    }

    return data.data;
}

export const createToken = async (userToken: string, branch: string, token: IApiTokenInput): Promise<IApiToken> => {
    const response = await fetch(getBaseUrl(branch), {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(token),
    });

    const data: IApiTokenOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to create token.`);
    }

    return data.data;
};

export const updateToken = async (userToken: string, branch: string, id: string, token: IApiTokenInput): Promise<IApiToken> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'PUT',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(token),
    });

    const data: IApiTokenOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to update token.`);
    }

    return data.data;
};

export const deleteToken = async (userToken: string, branch: string, id: string): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to delete token.`);
    }

    return data;
}

export const addTokenCategory = async (userToken: string, branch: string, id: string, categoryId: string): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            category_id: categoryId
        }),
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to add category ${categoryId} to token with id: ${id}`);
    }

    return data;
}

export const deleteTokenCategory = async (userToken: string, branch: string, id: string, categoryId: string): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category/${categoryId}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to remove category ${categoryId} from token with id: ${id}`);
    }

    return data;
}

export const rollToken = async (userToken: string, branch: string, id: string): Promise<IApiToken> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/roll`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
    });

    const data: IApiTokenOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to roll token with id: ${id}`);
    }

    return data.data;
}

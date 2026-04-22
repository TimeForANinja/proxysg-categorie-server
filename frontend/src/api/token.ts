import {IApiToken, IApiTokenCreateInput, IApiTokenUpdateInput, IApiTokenOutput, IListTokenOutput, IRestTokenDetail} from "../types/apiToken";
import {GenericOutput} from "../types/api";


export const getTokens = async (userToken: string, branch: string, addMappings: boolean = false, addLastUsed: boolean = false): Promise<IRestTokenDetail[]> => {
    const response = await fetch(`/api/branch/${branch}/token?add_mappings=${addMappings}&add_last_used=${addLastUsed}`, {
        headers: { 'jwt-token': userToken },
    });
    const data: IListTokenOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get tokens`);
    }

    return data.data;
}

export const createToken = async (userToken: string, token: IApiTokenCreateInput): Promise<IApiToken> => {
    const response = await fetch(`/api/branch/@me/token`, {
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

export const updateToken = async (userToken: string, id: string, token: IApiTokenUpdateInput): Promise<IApiToken> => {
    const response = await fetch(`/api/branch/@me/token/${id}`, {
        method: 'PATCH',
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

export const rollToken = async (userToken: string, id: string): Promise<IApiToken> => {
    const response = await fetch(`/api/branch/@me/token/${id}/roll`, {
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

export const deleteToken = async (userToken: string, id: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/token/${id}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to delete token.`);
    }

    return data;
}


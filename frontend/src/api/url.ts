import {IListURLOutput, IRestURLDetail, IURLOutput, IURL, IURLCreateInput, IURLUpdateInput} from "../types/url";
import {GenericOutput} from "../types/api";


export const getURLs = async (userToken: string, branch: string, addMappings: boolean = false, addBCCat: boolean = false): Promise<IRestURLDetail[]> => {
    const response = await fetch(`/api/branch/${branch}/url?add_mappings=${addMappings}&add_bc_cat=${addBCCat}`, {
        headers: { 'jwt-token': userToken },
    });
    const data: IListURLOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get URLs`);
    }

    return data.data;
}

export const createURL = async (userToken: string, input: IURLCreateInput): Promise<IURL> => {
    const response = await fetch(`/api/branch/@me/url`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
    });

    const data: IURLOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to create URL ${input.url}`);
    }

    return data.data;
}

export const updateURL = async (userToken: string, urlId: string, input: IURLUpdateInput): Promise<IURL> => {
    const response = await fetch(`/api/branch/@me/url/${urlId}`, {
        method: 'PATCH',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
    });

    const data: IURLOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to update URL ${urlId}`);
    }

    return data.data;
}

export const deleteURL = async (userToken: string, urlId: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/url/${urlId}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to delete URL ${urlId}`);
    }

    return data;
}


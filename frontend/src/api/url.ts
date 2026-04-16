import {IListURLOutput, IRestURLDetail, IURLCategoryMappingInput, IURLOutput, IURL} from "../types/url";
import {GenericOutput} from "../types/api";

const getBaseUrl = (branch: string) => `/api/branch/${branch}`;

export const getURLs = async (userToken: string, branch: string): Promise<IRestURLDetail[]> => {
    const response = await fetch(`${getBaseUrl(branch)}/url`, {
        headers: { 'jwt-token': userToken },
    });
    const data: IListURLOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get URLs`);
    }

    return data.data;
}

export const createURL = async (userToken: string, branch: string, url: string): Promise<IURL> => {
    const response = await fetch(`${getBaseUrl(branch)}/url`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
    });

    const data: IURLOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to create URL ${url}`);
    }

    return data.data;
}

export const updateURL = async (userToken: string, branch: string, urlId: string, url: string): Promise<IURL> => {
    const response = await fetch(`${getBaseUrl(branch)}/url/${urlId}`, {
        method: 'PUT',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
    });

    const data: IURLOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to update URL ${urlId}`);
    }

    return data.data;
}

export const deleteURL = async (userToken: string, branch: string, urlId: string): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/url/${urlId}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to delete URL ${urlId}`);
    }

    return data;
}

export const addURLCategory = async (userToken: string, branch: string, categoryId: string, mapping: IURLCategoryMappingInput): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/category/${categoryId}/url`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(mapping),
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to add url ${mapping.url} to category ${categoryId}`);
    }

    return data;
}

export const deleteURLCategory = async (userToken: string, branch: string, categoryId: string, url: string): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/category/${categoryId}/url/${url}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to remove url ${url} from category ${categoryId}`);
    }

    return data;
}

import {IListURLOutput, IRestURLDetail, IURLCategoryMappingInput, IURLOutput, IURL} from "../types/url";
import {GenericOutput} from "../types/api";


export const getURLs = async (userToken: string, branch: string): Promise<IRestURLDetail[]> => {
    const response = await fetch(`/api/branch/${branch}/url`, {
        headers: { 'jwt-token': userToken },
    });
    const data: IListURLOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get URLs`);
    }

    return data.data;
}

export const createURL = async (userToken: string, url: string): Promise<IURL> => {
    const response = await fetch(`/api/branch/@me/url`, {
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

export const updateURL = async (userToken: string, urlId: string, url: string): Promise<IURL> => {
    const response = await fetch(`/api/branch/@me/url/${urlId}`, {
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


export const addURLCategory = async (userToken: string, categoryId: string, mapping: IURLCategoryMappingInput): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/category/${categoryId}/url`, {
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

export const deleteURLCategory = async (userToken: string, categoryId: string, url: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/category/${categoryId}/url/${url}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to remove url ${url} from category ${categoryId}`);
    }

    return data;
}

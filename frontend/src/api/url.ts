import {IListURLOutput, IRestURLDetail, IURLCategoryMappingInput} from "../types/url";
import {GenericOutput} from "../types/api";

const getBaseUrl = (branch: string) => `/api/branch/${branch}`;

export const getURLs = async (branch: string): Promise<IRestURLDetail[]> => {
    const response = await fetch(`${getBaseUrl(branch)}/url`);
    const data: IListURLOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get URLs`);
    }

    return data.data;
}

export const addURLCategory = async (branch: string, categoryId: string, mapping: IURLCategoryMappingInput): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/category/${categoryId}/url`, {
        method: 'POST',
        headers: {
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

export const deleteURLCategory = async (branch: string, categoryId: string, url: string): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/category/${categoryId}/url/${url}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to remove url ${url} from category ${categoryId}`);
    }

    return data;
}

import {URLMapping} from "../types/url";

const getBaseUrl = (branch: string) => `/api/branch/${branch}`;

export const getURLs = async (branch: string): Promise<URLMapping[]> => {
    const response = await fetch(`${getBaseUrl(branch)}/url`);

    if (!response.ok) {
        throw new Error(`Failed to get URLs`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const addURLCategory = async (branch: string, url: string, categoryId: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/category/${categoryId}/url`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: url,
        }),
    });

    if (!response.ok) {
        throw new Error(`Failed to add url ${url} to category ${categoryId}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const deleteURLCategory = async (branch: string, url: string, categoryId: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/category/${categoryId}/url/${url}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to remove url ${url} to category ${categoryId}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

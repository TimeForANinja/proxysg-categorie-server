import {IUrl, IMutableUrl} from "../model/types/url";

const getBaseUrl = (branch: string) => `/api/branch/${branch}/url`;

export const getURLs = async (branch: string): Promise<IUrl[]> => {
    const response = await fetch(getBaseUrl(branch));

    if (!response.ok) {
        throw new Error(`Failed to get URLs`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const updateURL = async (branch: string, id: string, updatedURL: IMutableUrl): Promise<IUrl> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedURL),
    });

    if (!response.ok) {
        throw new Error(`Failed to update url with id: ${id}`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
};

export const createURL = async (branch: string, partialURL: IMutableUrl): Promise<IUrl> => {
    const response = await fetch(getBaseUrl(branch), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(partialURL),
    });

    if (!response.ok) {
        throw new Error(`Failed to create url.`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
};

export const deleteURL = async (branch: string, id: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Failed to delete URL.`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
};

export const addURLCategory = async (branch: string, id: string, categoryId: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category/${categoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to add category ${categoryId} to url with id: ${id}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const deleteURLCategory = async (branch: string, id: string, categoryId: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category/${categoryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to remove category ${categoryId} from url with id: ${id}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const setURLCategory = async (branch: string, id: string, categories: string[]): Promise<string[]> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}/category`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ categories }),
    });

    if (!response.ok) {
        throw new Error(`Failed to set categories ${categories.join(',')} for url with id: ${id}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

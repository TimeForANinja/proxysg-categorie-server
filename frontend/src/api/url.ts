import {IUrl, IMutableUrl} from "../model/types/url";

const URL_BASE_URL = '/api/url'

export const getURLs = async (userToken: string): Promise<IUrl[]> => {
    const response = await fetch(URL_BASE_URL, {
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        throw new Error(`Failed to get URLs`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const updateURL = async (userToken: string, id: string, updatedURL: IMutableUrl): Promise<IUrl> => {
    const response = await fetch(`${URL_BASE_URL}/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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

export const createURL = async (userToken: string, partialURL: IMutableUrl): Promise<IUrl> => {
    const response = await fetch(URL_BASE_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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

export const deleteURL = async (userToken: string, id: string): Promise<void> => {
    const response = await fetch(`${URL_BASE_URL}/${id}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        throw new Error(`Failed to delete URL.`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
};

export const addURLCategory = async (userToken: string, id: string, categoryId: string): Promise<void> => {
    const response = await fetch(`${URL_BASE_URL}/${id}/category/${categoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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

export const deleteURLCategory = async (userToken: string, id: string, categoryId: string): Promise<void> => {
    const response = await fetch(`${URL_BASE_URL}/${id}/category/${categoryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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

export const setURLCategory = async (userToken: string, id: string, categories: string[]): Promise<string[]> => {
    const response = await fetch(`${URL_BASE_URL}/${id}/category`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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

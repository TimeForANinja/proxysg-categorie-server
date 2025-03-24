export interface IMutableURL {
    hostname: string;
}

export interface IURL extends IMutableURL {
    id: number;
    hostname: string;
    categories: number[];
}
    
export const getURLs = async (): Promise<IURL[]> => {
    const response = await fetch('/api/url');
    const data = await response.json();
    return data.data;
}

export const updateURL = async (id: Number, updatedURL: IMutableURL): Promise<IURL> => {
    const response = await fetch(`/api/url/${id}`, {
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
    return data.data;
};

export const createURL = async (partialURL: IMutableURL): Promise<IURL> => {
    const response = await fetch(`/api/url`, {
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
    return data.data;
};

export const deleteURL = async (id: number): Promise<void> => {
    const response = await fetch(`/api/url/${id}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Failed to delete URL.`);
    }
};

export const addURLCategory = async (id: number, categoryId: number): Promise<void> => {
    const response = await fetch(`/api/url/${id}/category/${categoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to add category ${categoryId} to url with id: ${id}`);
    }
}

export const deleteURLCategory = async (id: number, categoryId: number): Promise<void> => {
    const response = await fetch(`/api/url/${id}/category/${categoryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to remove category ${categoryId} from url with id: ${id}`);
    }
}

export const setURLCategory = async (id: number, categories: number[]): Promise<number[]> => {
    const response = await fetch(`/api/url/${id}/category`, {
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
    return data.data;
}

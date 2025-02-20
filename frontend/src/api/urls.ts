export interface IURL {
    id: number;
    hostname: string;
    categories: number[];
}

export const getURLs = async (): Promise<IURL[]> => {
    const response = await fetch('http://127.0.0.1:3080/api/urls');
    const data = await response.json();
    return data.data;
}

export const updateURL = async (updatedURL: IURL): Promise<IURL> => {
    const response = await fetch(`http://127.0.0.1:3080/api/urls/${updatedURL.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedURL),
    });

    if (!response.ok) {
        throw new Error(`Failed to update url with id: ${updatedURL.id}`);
    }

    const data = await response.json();
    return data.data;
};

export const createURL = async (partialURL: IURL): Promise<IURL> => {
    const response = await fetch(`http://127.0.0.1:3080/api/urls`, {
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

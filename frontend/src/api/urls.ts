
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


export interface IAtomic {
    id: number;
    action: string;
}

export interface ICommits {
    id: number;
    time: number;
    name: string;
    atomics: IAtomic[];
}


export const getHistory = async (url_id: number): Promise<ICommits[]> => {
    const response = await fetch(`http://127.0.0.1:3080/api/history/${url_id}`);
    const data = await response.json();
    return data.data;
}

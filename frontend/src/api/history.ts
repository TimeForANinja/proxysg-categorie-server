
export interface IAtomic {
    id: number;
    action: string;
}

export interface ICommits {
    id: number;
    time: number;
    description: string;
    atomics: IAtomic[];
}


export const getHistory = async (): Promise<ICommits[]> => {
    const response = await fetch('/api/history');
    const data = await response.json();
    return data.data;
}

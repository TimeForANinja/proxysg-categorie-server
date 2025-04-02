
export interface IAtomic {
    id: string;
    action: string;
}

export interface ICommits {
    id: string;
    time: number;
    description: string;
    atomics: IAtomic[];
}


export const getHistory = async (userToken: string): Promise<ICommits[]> => {
    const response = await fetch('/api/history', {
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        throw new Error(`Failed to get history`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

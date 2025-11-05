/**
 * Utility interface for generalizing data thats referencing other entries
 * e.g.: a commit or atomic that has a reference to the url/category/token it was created for
 */
export interface IReferred {
    ref_token: string[];
    ref_url: string[];
    ref_category: string[];
}

export interface IAtomic extends IReferred {
    id: string;
    action: string;
    description: string;
    user: string;
    timestamp: number;
}

export interface ICommits extends IReferred {
    id: string;
    time: number;
    description: string;
    user: string;
    atomics: IAtomic[];
}

const HISTORY_BASE_URL = '/api/history'

export const getHistory = async (userToken: string): Promise<ICommits[]> => {
    const response = await fetch(HISTORY_BASE_URL, {
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

import {ICommit} from "../types/history";

const baseUrl = '/api/branch'

export const getHistory = async (branch: string): Promise<ICommit[]> => {
    const response = await fetch(`${baseUrl}/${branch}/history`);

    if (!response.ok) {
        throw new Error(`Failed to get history`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const getBranches = async (): Promise<string[]> => {
    const response = await fetch(baseUrl);

    if (!response.ok) {
        throw new Error(`Failed to get branch list`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const resetBranches = async (): Promise<void> => {
    const response = await fetch('/api/me/reset-branch', {
        method: 'POST',
    });

    if (!response.ok) {
        throw new Error(`Failed to get branch list`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return;
}

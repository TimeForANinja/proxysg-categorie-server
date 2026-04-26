import {IRestBranchInfo, IListBranchesOutput} from "../types/branch";
import {GenericOutput} from "../types/api";


export const getBranches = async (userToken: string): Promise<IRestBranchInfo[]> => {
    const response = await fetch('/api/branch', {
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        const data: IListBranchesOutput = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to get branch list`);
    }

    const data: IListBranchesOutput = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to get branch list`);
    }

    return data.data;
}

export const resetBranches = async (userToken: string): Promise<GenericOutput> => {
    const response = await fetch('/api/branch/@me/reset', {
        method: 'POST',
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        const data: GenericOutput = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to reset branches`);
    }

    const data: GenericOutput = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to reset branches`);
    }

    return data;
}

export const doCommit = async (userToken: string, message: string): Promise<GenericOutput> => {
    const response = await fetch('/api/branch/@me/commit', {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
    });

    if (!response.ok) {
        const data: GenericOutput = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to commit changes`);
    }

    const data: GenericOutput = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to commit changes`);
    }

    return data;
}

export const loadExisting = async (
    userToken: string,
    text: string,
    prefix: string,
): Promise<GenericOutput> => {
    const response = await fetch(`api/branch/@me/import`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
        body: JSON.stringify({
            category_db: text,
            prefix,
        }),
    });

    if (!response.ok) {
        const data: GenericOutput = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to import category database`);
    }

    const data: GenericOutput = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to import category database`);
    }

    return data;
}


export const cleanupBranch = async (userToken: string): Promise<GenericOutput> => {
    const response = await fetch('/api/branch/@me/cleanup', {
        method: 'POST',
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        const data: GenericOutput = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to cleanup branch`);
    }

    const data: GenericOutput = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to cleanup branch`);
    }

    return data;
}

import {IRestBranchInfo, IListBranchesOutput} from "../types/branch";
import {GenericOutput} from "../types/api";

const baseUrl = '/api/branch';

export const getBranches = async (): Promise<IRestBranchInfo[]> => {
    const response = await fetch(baseUrl);
    const data: IListBranchesOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get branch list`);
    }

    return data.data;
}

export const resetBranches = async (): Promise<GenericOutput> => {
    const response = await fetch('/api/me/reset-branch', {
        method: 'POST',
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to reset branches`);
    }

    return data;
}

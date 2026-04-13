import {IRestCommit, IListHistoryOutput} from "../types/history";

const baseUrl = '/api/branch';

export const getHistory = async (branch: string): Promise<IRestCommit[]> => {
    const response = await fetch(`${baseUrl}/${branch}/history`);
    const data: IListHistoryOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get history`);
    }

    return data.data;
}

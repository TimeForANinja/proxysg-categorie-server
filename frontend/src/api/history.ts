import {IRestCommit, IListHistoryOutput} from "../types/history";

const baseUrl = '/api/branch';

interface IHistoryInput {
    filter_uuid?: string[];
}

export const getHistory = async (branch: string, filter_uuid?: string[]): Promise<IRestCommit[]> => {
    let body: IHistoryInput = {}
    if (filter_uuid) body['filter_uuid'] = filter_uuid;

    const response = await fetch(`${baseUrl}/${branch}/history`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    });
    const data: IListHistoryOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get history`);
    }

    return data.data;
}

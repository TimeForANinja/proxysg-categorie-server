import {IRestCommit, IListHistoryOutput} from "../types/history";


interface IHistoryInput {
    filter_uuid?: string[];
}


export const getHistory = async (userToken: string, branch: string, filter_uuid?: string[]): Promise<IRestCommit[]> => {
    let body: IHistoryInput = {}
    if (filter_uuid) body['filter_uuid'] = filter_uuid;

    const response = await fetch(`/api/branch/${branch}/history`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const data: IListHistoryOutput = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to get history`);
    }

    const data: IListHistoryOutput = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to get history`);
    }

    return data.data;
}

import {IUrl} from "../model/types/url";
import {ICategory} from "../model/types/category";

const BASE_URL = '/api'

export interface TestReply {
    input: string;
    matched_url: IUrl;
    local_categories: ICategory[];
    bc_categories: string[];
}


export const runTest = async (userToken: string, value: string): Promise<TestReply> => {
    const response = await fetch(`${BASE_URL}/test-uri/${value}`, {
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        throw new Error(`Failed to get run test`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

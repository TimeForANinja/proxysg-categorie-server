import {DataOutput} from "./api";

export interface IRestCommit {
    uuid: string;
    description: string;
    author: string;
    created_at: number;
    parent_commit?: string;
}

export interface IDiffOutput {
    status: 'success' | 'failed';
    message: string;
    data: string;
}

export type IListHistoryOutput = DataOutput<IRestCommit[]>;

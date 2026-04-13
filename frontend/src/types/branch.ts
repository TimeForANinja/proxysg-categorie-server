import {DataOutput} from "./api";

export interface IRestBranchInfo {
    name: string;
    permission: string;
}

export type IListBranchesOutput = DataOutput<IRestBranchInfo[]>;

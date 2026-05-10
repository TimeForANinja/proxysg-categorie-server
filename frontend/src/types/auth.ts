import {DataOutput} from "./api";

export interface IUser {
    username: string;
    roles: string[];
}

export interface ILoginOutputData {
    user: IUser;
    token: string;
}

export type ILoginOutput = DataOutput<ILoginOutputData>;


export interface IAuthUIComponent {
    type: "button" | "input-text" | "input-password" | string;
    label?: string;
    key?: string;
    location?: string;
}

export interface IAuthMechanism {
    type: string;
    label: string;
    ui: IAuthUIComponent[];
}

export type IAuthMechanismsOutput = DataOutput<IAuthMechanism[]>;

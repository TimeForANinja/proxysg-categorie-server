import {StringKV} from "./stringKV";
import {FieldDefinition, SHARED_DEFINITIONS} from "../searchParser/fieldDefinition";
import {ICategory} from "./category";
import {DataOutput} from "./api";
import {formatUnixTimestamp} from "../util/DateString";

export interface IApiToken {
    id: string;
    token_value: string;
    description: string;
}

export interface IApiTokenCreateInput {
    description: string;
}

export interface IApiTokenUpdateInput {
    description?: string;
}

export interface IRestTokenDetail {
    token: IApiToken;
    categories: ICategory[];
    last_used: number;
}

export type IApiTokenOutput = DataOutput<IApiToken>;
export type IListTokenOutput = DataOutput<IRestTokenDetail[]>;

export const ApiTokenToKV = (x: IRestTokenDetail): StringKV => {
    return {
        id: x.token.id,
        value: x.token.token_value,
        description: x.token.description,
        cats: x.categories.map(c => c.name).join(', '),
        categories: x.categories.map(c => c.name).join(', '),
        last_used: formatUnixTimestamp(x.last_used),
    };
}

export const ApiTokenFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "value", description: "Token Value itself" },
    SHARED_DEFINITIONS.description,
    SHARED_DEFINITIONS.cats,
    SHARED_DEFINITIONS.categories,
    { field: "last_used", description: "Last Used" },
]

export const ApiTokenFieldsRaw: FieldDefinition[] = [
    ...ApiTokenFields,
    SHARED_DEFINITIONS.raw,
]

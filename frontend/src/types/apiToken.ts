import {StringKV} from "./stringKV";
import {FieldDefinition, SHARED_DEFINITIONS} from "../searchParser/fieldDefinition";

export interface IMutableApiToken {
    description: string;
}

export interface IApiToken extends IMutableApiToken {
    id: string;
    token_value: string;
    categories: string[];
}

const TIME_SECONDS = 1000;

export const parseLastUsed = (last_use: number): string => {
    if (last_use === 0) {
        return 'never';
    } else {
        return new Date(last_use * TIME_SECONDS).toLocaleString();
    }
}

export const ApiTokenToKV = (x: IApiToken): StringKV => {
    return {
        id: x.id,
        value: x.token_value,
        description: x.description,
        cats: x.categories.join(', '),
        categories: x.categories.join(', '),
    };
}

export const ApiTokenFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "value", description: "Token Value itself" },
    SHARED_DEFINITIONS.description,
    SHARED_DEFINITIONS.cats,
    SHARED_DEFINITIONS.categories,
]
export const ApiTokenFieldsRaw: FieldDefinition[] = [
    ...ApiTokenFields,
    SHARED_DEFINITIONS.raw,
]

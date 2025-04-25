import {StringKV} from "./stringKV";
import {FieldDefinition, SHARED_DEFINITIONS} from "../../searchParser/fieldDefinition";
import {LUT} from "./LookUpTable";
import {ICategory} from "./category";

export interface IMutableApiToken {
    description: string;
}

export interface IApiToken extends IMutableApiToken {
    id: string;
    token: string;
    categories: string[];
    last_use: number;
}

const TIME_SECONDS = 1000;

export const parseLastUsed = (last_use: number): string => {
    if (last_use === 0) {
        return 'never';
    } else {
        return new Date(last_use * TIME_SECONDS).toLocaleString();
    }
}

export const ApiTokenToKV = (x: IApiToken, categories: LUT<ICategory>): StringKV => {
    const cats = x.categories.map(c => categories[c]?.name).join(',');
    return {
        id: x.id,
        token: x.token,
        description: x.description,
        last_use: parseLastUsed(x.last_use),
        cats: cats,
        categories: cats,
        cat_ids: x.categories.join(','),
    };
}

export const ApiTokenFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "token", description: "Token" },
    SHARED_DEFINITIONS.description,
    { field: "last_use", description: "Date the Token was last used" },
    SHARED_DEFINITIONS.cats,
    SHARED_DEFINITIONS.categories,
]
export const ApiTokenFieldsRaw: FieldDefinition[] = [
    ...ApiTokenFields,
    SHARED_DEFINITIONS.raw,
]

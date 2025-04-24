import {StringKV} from "./str_kv";
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
    return {
        id: x.id,
        token: x.token,
        description: x.description,
        last_use: parseLastUsed(x.last_use),
        cats: x.categories.map(c => categories[c]?.name).join(','),
        cat_ids: x.categories.join(','),
    };
}

import {LUT} from "./LookUpTable";
import {StringKV} from "./str_kv";
import {FieldDefinition, SHARED_DEFINITIONS} from "./fieldDefinition";
import {ICategory} from "./category";

export interface IMutableURL {
    hostname: string;
    description: string;
}

export interface IURL extends IMutableURL {
    id: string;
    categories: string[];
    bc_cats: string[];
}

export const UrlToKV = (x: IURL, categories: LUT<ICategory>): StringKV => {
    return {
        id: x.id,
        host: x.hostname,
        description: x.description,
        cats: x.categories.map(c => categories[c]?.name).join(','),
        cat_ids: x.categories.join(','),
        bc_cats: x.bc_cats.join(','),
    };
}

export const UrlFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "host", description: "Hostname/domain" },
    SHARED_DEFINITIONS.description,
    SHARED_DEFINITIONS.cats,
    { field: "bc_cats", description: "Blue Coat categories" },
]

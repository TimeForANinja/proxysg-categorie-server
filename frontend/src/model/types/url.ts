import {LUT} from "./LookUpTable";
import {StringKV} from "./stringKV";
import {FieldDefinition, SHARED_DEFINITIONS} from "./fieldDefinition";
import {ICategory} from "./category";

export interface IMutableUrl {
    hostname: string;
    description: string;
}

export interface IUrl extends IMutableUrl {
    id: string;
    categories: string[];
    bc_cats: string[];
}

export const UrlToKV = (x: IUrl, categories: LUT<ICategory>): StringKV => {
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

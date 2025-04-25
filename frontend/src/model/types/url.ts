import {LUT} from "./LookUpTable";
import {StringKV} from "./stringKV";
import {FieldDefinition, SHARED_DEFINITIONS} from "../../searchParser/fieldDefinition";
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
    const cats = x.categories.map(c => categories[c]?.name).join(',');
    return {
        id: x.id,
        host: x.hostname,
        description: x.description,
        cats: cats,
        categories: cats,
        cat_ids: x.categories.join(','),
        bc_cats: x.bc_cats.join(','),
    };
}

export const UrlFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "host", description: "Hostname/domain" },
    SHARED_DEFINITIONS.description,
    SHARED_DEFINITIONS.cats,
    SHARED_DEFINITIONS.categories,
    { field: "bc_cats", description: "Blue Coat categories" },
]
export const UrlFieldsRaw: FieldDefinition[] = [
    ...UrlFields,
    SHARED_DEFINITIONS.raw,
]

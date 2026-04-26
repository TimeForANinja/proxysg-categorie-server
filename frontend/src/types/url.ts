import {StringKV} from "./stringKV";
import {FieldDefinition, SHARED_DEFINITIONS} from "../searchParser/fieldDefinition";
import {ICategory} from "./category";
import {DataOutput} from "./api";
import {formatConstraint} from "../util/DateString";

export interface IURL {
    id: string;
    url: string;
    description: string;
}

export interface IURLCreateInput {
    url: string;
    description?: string;
}

export interface IURLUpdateInput {
    url?: string;
    description?: string;
}

export interface IConstraint {
    comment: string;
    start: number;
    end: number;
}

export interface IRestConstrainedURL {
    url: IURL;
    constraint?: IConstraint;
}

export interface IRestConstrainedCategory {
    category: ICategory;
    constraint?: IConstraint;
}

export interface IURLCategoryMappingInput {
    url_id: string;
    constraint?: IConstraint;
}

export interface IBCCategory {
    categories: string[];
    last_changed: number;
    last_checked: number;
    url_value: string;
}

export interface IRestURLDetail {
    url: IURL;
    categories: IRestConstrainedCategory[];
    bc_category?: IBCCategory;
}

export type IURLOutput = DataOutput<IURL>;
export type IListURLOutput = DataOutput<IRestURLDetail[]>;

export const URLMappingToKV = (x: IRestURLDetail): StringKV => {
    return {
        id: x.url.id,
        url: x.url.url,
        description: x.url.description,
        cats: x.categories.map(x => x.category.name).join(', '),
        categories: x.categories.map(c => c.category.name).join(', '),
        has_constraints: x.categories.find(x => x.constraint) ? 'true' : 'false',
        constraints: x.categories.filter(x => x.constraint).map(x => formatConstraint(x.constraint)).join(', '),
        bc_cats: x.bc_category?.categories.join(', ') || '',
    };
}

export const URLMappingFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "url", description: "Value of the URL" },
    SHARED_DEFINITIONS.description,
    SHARED_DEFINITIONS.cats,
    SHARED_DEFINITIONS.categories,
    { field: "bc_cats", description: "Bluecoat Categories" },
    { field: "has_constraints", description: "\True\" if any mapped category is constrained" },
    { field: "constraints", description: "List of all constraints" },
]

export const UrlMappingFieldsRaw: FieldDefinition[] = [
    ...URLMappingFields,
    SHARED_DEFINITIONS.raw,
]

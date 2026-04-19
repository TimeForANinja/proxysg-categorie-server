import {StringKV} from "./stringKV";
import {FieldDefinition, SHARED_DEFINITIONS} from "../searchParser/fieldDefinition";
import {ICategory} from "./category";
import {DataOutput} from "./api";

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

export interface IRestURLDetail {
    url: IURL;
    categories: IRestConstrainedCategory[];
}

export type IURLOutput = DataOutput<IURL>;
export type IListURLOutput = DataOutput<IRestURLDetail[]>;

export const URLMappingToKV = (x: IRestURLDetail): StringKV => {
    return {
        id: x.url.id,
        url: x.url.url,
        cats: x.categories.map(x => x.category.name).join(', '),
        categories: x.categories.map(c => c.category.name).join(', '),
    };
}

export const URLMappingFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "url", description: "Value of the URL" },
    SHARED_DEFINITIONS.cats,
    SHARED_DEFINITIONS.categories,
]

export const UrlMappingFieldsRaw: FieldDefinition[] = [
    ...URLMappingFields,
    SHARED_DEFINITIONS.raw,
]

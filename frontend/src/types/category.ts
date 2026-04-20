import {FieldDefinition, SHARED_DEFINITIONS} from "../searchParser/fieldDefinition";
import {StringKV} from "./stringKV";
import {DataOutput} from "./api";

export interface ICategory {
    id: string;
    name: string;
    description: string;
    color: number;
}

export interface ICategoryCreateInput {
    name: string;
    description: string;
    color?: number;
}

export interface ICategoryUpdateInput {
    name?: string;
    description?: string;
    color?: number;
}

export interface IRestCategoryDetail {
    category: ICategory;
    children: ICategory[];
}

export type ICategoryOutput = DataOutput<ICategory>;
export type IListCategoryOutput = DataOutput<ICategory[]>;
export type IListCategoryDetailsOutput = DataOutput<IRestCategoryDetail[]>;

export const CategoryToKV = (x: ICategory): StringKV => {
    return {
        id: x.id,
        name: x.name,
        description: x.description,
        color: x.color.toString(),
    }
}

export const CategoryFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "name", description: "Name" },
    SHARED_DEFINITIONS.description,
    { field: "color", description: "Color" },
]

export const CategoryFieldsRaw: FieldDefinition[] = [
    ...CategoryFields,
    SHARED_DEFINITIONS.raw,
]

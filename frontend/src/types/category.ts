import {FieldDefinition, SHARED_DEFINITIONS} from "../searchParser/fieldDefinition";
import {StringKV} from "./stringKV";
import {DataOutput} from "./api";

export interface ICategory {
    id: string;
    name: string;
}

export interface ICategoryInput {
    name: string;
}

export type IMutableCategory = ICategoryInput;

export type ICategoryOutput = DataOutput<ICategory>;
export type IListCategoryOutput = DataOutput<ICategory[]>;

export const CategoryToKV = (x: ICategory): StringKV => {
    return {
        id: x.id,
        name: x.name,
    }
}

export const CategoryFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "name", description: "Name" },
]

export const CategoryFieldsRaw: FieldDefinition[] = [
    ...CategoryFields,
    SHARED_DEFINITIONS.raw,
]

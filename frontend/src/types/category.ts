import {FieldDefinition, SHARED_DEFINITIONS} from "../searchParser/fieldDefinition";
import {StringKV} from "./stringKV";

export interface IMutableCategory {
    name: string;
}

export interface ICategory extends IMutableCategory {
    id: string;
    members: string[];
}

export const CategoryToKV = (x: ICategory): StringKV => {
    return {
        id: x.id,
        name: x.name,
        members: x.members.join(', '),
    }
}

export const CategoryFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "name", description: "Name" },
    { field: "members", description: "CSV of member category names" },
]
export const CategoryFieldsRaw: FieldDefinition[] = [
    ...CategoryFields,
    SHARED_DEFINITIONS.raw,
]

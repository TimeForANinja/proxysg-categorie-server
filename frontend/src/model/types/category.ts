import {FieldDefinition, SHARED_DEFINITIONS} from "./fieldDefinition";
import {StringKV} from "./stringKV";
import {LUT} from "./LookUpTable";
import {colorLUT} from "../../util/colormixer";

export interface IMutableCategory {
    name: string;
    color: number;
    description: string;
}

export interface ICategory extends IMutableCategory {
    id: string;
    nested_categories: string[];
}

export const CategoryToKV = (x: ICategory, categories: LUT<ICategory>): StringKV => {
    return {
        id: x.id,
        name: x.name,
        color: colorLUT[x.color].name,
        description: x.description,
        cats: x.nested_categories.map(c => categories[c]?.name).join(','),
        cat_ids: x.nested_categories.join(','),
    }
}

export const CategoryFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "name", description: "Name" },
    { field: "color", description: "Color" },
    SHARED_DEFINITIONS.description,
    SHARED_DEFINITIONS.cats,
]

import {FieldDefinition, SHARED_DEFINITIONS} from "../../searchParser/fieldDefinition";
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
    pending_changes: boolean;
}

export const CategoryToKV = (x: ICategory, categories: LUT<ICategory>): StringKV => {
    const cats = x.nested_categories.map(c => categories[c]?.name).join(',');
    return {
        id: x.id,
        name: x.name,
        color: colorLUT[x.color].name,
        description: x.description,
        cats: cats,
        categories: cats,
        cat_ids: x.nested_categories.join(','),
        changed: x.pending_changes ? 'true' : 'false',
    }
}

export const CategoryFields: FieldDefinition[] = [
    SHARED_DEFINITIONS.id,
    { field: "name", description: "Name" },
    { field: "color", description: "Color" },
    SHARED_DEFINITIONS.description,
    SHARED_DEFINITIONS.cats,
    SHARED_DEFINITIONS.categories,
    SHARED_DEFINITIONS.changed,
]
export const CategoryFieldsRaw: FieldDefinition[] = [
    ...CategoryFields,
    SHARED_DEFINITIONS.raw,
]

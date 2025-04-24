import {StringKV} from "./str_kv";
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

import {StringKV} from "./stringKV";
import {FieldDefinition, SHARED_DEFINITIONS} from "../searchParser/fieldDefinition";

export interface URLMapping {
    url: string;
    categories: string[];
}

export const URLMappingToKV = (x: URLMapping): StringKV => {
    return {
        url: x.url,
        categories: x.categories.join(', '),
    };
}

export const URLMappingFields: FieldDefinition[] = [
    { field: "url", description: "Value of the URL" },
    SHARED_DEFINITIONS.cats,
    SHARED_DEFINITIONS.categories,
]
export const UrlMappingFieldsRaw: FieldDefinition[] = [
    ...URLMappingFields,
    SHARED_DEFINITIONS.raw,
]

/**
 * A FieldDefinition provides details about properties of an Object.
 * It is used in combination with the SearchParser to filter Tables.
 * The Details here are designed to help the user identify and pick the right field.
 */
export type FieldDefinition = {
    field: string,
    description?: string,
}

/**
 * Shared FieldDefinitions for common fields.
 * The _raw field is used to store a truncated version of all fields
 */
export const FIELD_DEFINITION_RAW: FieldDefinition = {
    field: "_raw",
    description: "All fields truncated into a single string",
}

/**
 * Shared FieldDefinitions for common fields.
 * The ID field is used to identify the object.
 */
export const FIELD_DEFINITION_ID: FieldDefinition = {
    field: "id",
    description: "Unique Identifier for the object",
}

/**
 * Shared FieldDefinitions for common fields.
 * The description field is used to store a user-defined description of the object.
 */
export const FIELD_DEFINITION_DESCRIPTION: FieldDefinition = {
    field: "description",
    description: "User-Defined Description of the object",
}

/**
 * Shared FieldDefinitions for common fields.
 * The Categories field is used to store (sub)categories the URL / TOKEN / CAT belongs to
 */
export const FIELD_DEFINITION_CATEGORIES: FieldDefinition = {
    field: "categories",
    description: "List of Categories the object belongs to",
}

/**
 * Shorthand for categories
 */
export const FIELD_DEFINITION_CATS: FieldDefinition = {
    field: "cats",
    description: "Shorthand for categories",
}

/**
 * Shared FieldDefinitions for common fields.
 */
export const SHARED_DEFINITIONS = {
    raw: FIELD_DEFINITION_RAW,
    id: FIELD_DEFINITION_ID,
    description: FIELD_DEFINITION_DESCRIPTION,
    categories: FIELD_DEFINITION_CATEGORIES,
    cats: FIELD_DEFINITION_CATS,
}

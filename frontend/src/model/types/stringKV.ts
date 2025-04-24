/**
 * A simple key-value map with string values.
 */
export type StringKV = {
    [key: string]: string;
};

/**
 * Converts a StringKV to the string value for a _raw field.
 * The _raw field is used to store the original string value of a "content" row in a table.
 * It makes it easier to search for any value in any field
 *
 * @param kv the StringKV to convert
 * @returns the _raw string value
 */
export const KVtoRAW = (kv: StringKV): string => {
    let raw = [];
    for (const [, value] of Object.entries(kv)) {
        raw.push(value);
    }
    return raw.join(' ');
}

/**
 * Converts a StringKV to a _raw field and adds it to the object.
 *
 * @param kv the StringKV to convert and add the _raw field to
 * @returns a new object with the _raw field added to it
 */
export const KVaddRAW = (kv: StringKV): {
    _raw: string,
    [key: string]: string,
} => {
    return {
        _raw: KVtoRAW(kv),
        ...kv,
    }
}

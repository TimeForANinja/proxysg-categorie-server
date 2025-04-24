/**
 * The result of a calculation can be a string, boolean, or number.
 */
export type CALC_RESULT = string | boolean | number;

/**
 * Represents a row of data with string keys and various value types.
 */
export type DATA_ROW = {
    [key: string]: CALC_RESULT,
    _raw: string,
}

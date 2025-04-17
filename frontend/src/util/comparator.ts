const parseId = (id: string) => {
    // Parse as base16
    // if the num is base10 the basic < or > comparison will still work, so this simplifies stuff
    const numericValue = parseInt(id, 16);
    // Fallback to none if parsing fails
    return isNaN(numericValue) ? null : numericValue;
};

/**
 * Comparator function for sorting or ordering objects with `id` properties.
 *
 * This function attempts to parse the `id` values as base-16 integers for numeric comparison.
 * If the parsed values are valid numbers, it returns the difference between them.
 * If either `id` cannot be parsed as a number, the function defaults to a lexicographical string comparison.
 *
 * @param {Object} a - The first object for the comparison with an `id` property.
 * @param {Object} b - The second object for the comparison with an `id` property.
 * @returns {number} A negative number if `a` should come before `b`,
 * a positive number if `b` should come before `a`,
 * or 0 if they are considered equal.
 */
export const BY_ID = (
    a: { id: string },
    b: { id: string },
): number => {
    // try to parse the values as base16 int
    const idA = parseId(a.id);
    const idB = parseId(b.id);
    if (idA !== null && idB !== null) {
        return idA - idB;
    }

    // default to string comparison
    return a.id.localeCompare(b.id);
}

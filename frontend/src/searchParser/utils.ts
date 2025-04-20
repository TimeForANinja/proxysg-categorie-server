/**
 * This file contains utility functions for the search parser.
 */

import { CALC_RESULT, DATA_ROW } from './types';

/**
 * The Character splitting Function Parameters
 */
export const FUNC_ARG_SEPARATOR = Object.freeze(',');

/**
 * Normalizes a given string by trimming whitespace, removing extra spaces
 * outside quoted sections, and removing spaces around mathematical symbols
 * (`<`, `=`, `>`), except when inside quoted sections.
 *
 * This function preserves quoted content by building an index of all quoted blocks,
 * allowing it to skip modification of any content within these blocks.
 *
 * @param {string} baseStr - The input string to normalize.
 * @returns {string} - The normalized string, with unnecessary whitespace removed
 *                     while preserving quoted sections.
 *
 * @example
 * // returns 'a = "quoted text with  spaces" < b'
 * normalize('  a   =   "quoted text with  spaces"   <   b  ');
 */
export const normalize = (baseStr: string) :string => {
    // remove leading and trailing spaces
    let escaped = baseStr.trim();

    // build an index of all parts that are in quotes and should therefore not be altered
    const quoteBlocks = [];
    for (let i = 0; i < escaped.length; i++) {
        if (escaped[i] === "\"") {
            const end = getQuoteEnd(escaped, i)
            if (end === -1) throw new Error('Mismatched quotes');
            quoteBlocks.push({ start: i, end});
            i = end;
        }
    }

    // get all cases of multiple spaces
    const matches01 = Array.from(escaped.matchAll(/\s+/g));
    for (const match of matches01.reverse()) {
        // create vars to make our live easier
        const MultiSpace_start = match.index!;
        const MultiSpace_end = match.index! + match[0].length
        const MultiSpace_length = match[0].length;
        // it is "escaped" if it falls within a quoted block
        let isEscaped = quoteBlocks.some(q => q.start <= MultiSpace_start && q.end >= MultiSpace_end);
        if (!isEscaped) {
            // replace the multiple whitespaces with a single space
            escaped = escaped.substring(0, MultiSpace_start) + " " + escaped.substring(MultiSpace_end)
            // offset quoted blocks that are after the just edited space to account for the removed characters
            for (const q of quoteBlocks) {
                if (q.start > MultiSpace_start) {
                    q.start -= MultiSpace_length - 1;
                    q.end -= MultiSpace_length - 1;
                }
            }
        }
    }

    // get all cases of spaces around math actions (<, =, >)
    const matches02 = Array.from(escaped.matchAll(/\s+([=<>])\s+/g));
    for (const match of matches02.reverse()) {
        // create vars to make our live easier
        const math_start = match.index!;
        const math_end = match.index! + match[0].length
        const math_action = match[1];
        // it is "escaped" if it falls within a quoted block
        let isEscaped = quoteBlocks.some(q => q.start <= math_start && q.end >= math_end);
        if (!isEscaped) {
            // replace the math + whitespaces with just the math action and no whitespaces
            escaped = escaped.substring(0, math_start) + math_action + escaped.substring(math_end)
            // offset quoted blocks that are after the just edited space to account for the removed characters
            for (const q of quoteBlocks) {
                if (q.start > math_start) {
                    q.start -= math_action.length - 1;
                    q.end -= math_action.length - 1;
                }
            }
        }
    }

    return escaped;
}

/**
 * Get the closing position based of a string start.
 *
 * This method respects escaped characters (e.g. \")
 *
 * @param baseStr The input string.
 * @param startIDX The index at which the string starts
 * @returns The index of the closing character (or end of the string)
 */
export const getQuoteEnd = (baseStr: string, startIDX: number): number => {
    let end = startIDX;
    while (++end < baseStr.length) {
        // Skip escaped characters (e.g., \" but also \\)
        if (baseStr[end] === '\\') {
            end++; // Skip the next character
            continue;
        }
        if (baseStr[end] === "\"") {
            break;
        }
    }
    // return -1 if last found char is not end of quote
    return baseStr[end] === "\"" ? end : -1;
};

/**
 * Get the closing of a brace.
 *
 * Uses a stack-based algorithm to track opening and closing characters,
 * allowing for nested braces and quotes.
 *
 * @param baseStr The input string.
 * @param startIDX The length of the prefix before the opening character.
 * @returns The index of the closing character or -1 if not found.
 */
export const getParenthesisEnd = (baseStr: string, startIDX: number): number => {
    let stack = 1;
    let end = startIDX;
    while (++end < baseStr.length) {
        // Skip escaped closing characters (e.g., \))
        if (baseStr[end] === '\\') {
            // Skip the next character
            end++;
            continue;
        }

        if (baseStr[end] === "\"") {
            // skip to end of string
            end = getQuoteEnd(baseStr, end);
            if (end === -1) throw new Error('Mismatched quotes');
            continue;
        }

        // Update stack for nested structures
        if (baseStr[end] === "(") {
            stack++;
        } else if (baseStr[end] === ")") {
            stack--;
        }
        // Check for end of stack
        if (stack === 0) {
            break;
        }
    }
    return stack === 0 ? end : -1; // Return -1 if not properly closed
};

/**
 * Cut into arguments based on the provided separator.
 *
 * Supports both braces (and nested braces) as well as explicit strings in quotations,
 * by using the getQuoteEnd() and ParenthesisEnd() functions
 *
 * @param baseStr the string inside the braces
 * @param separator the character(s) used to split the baseStr
 * @returns an array of arguments
 */
export const splitArgs = (baseStr: string, separator: string): string[] => {
    console.assert(separator.length === 1, 'separator must be a single character');

    // Custom trim to remove leading and trailing spaces and separators
    const baseStrTrimmed = baseStr.replace(new RegExp(`^[\\s${separator}]*(.*?)[\\s${separator}]*$`), '$1');

    // Holds the indices where the current split starts
    let startIndex = 0;

    // Collect the split substrings
    const splits = [];

    // Initialize loop counter
    let currentIndex = 0;

    // Convert separator to regex
    let separatorRegex = new RegExp(`[${separator}]`);

    while (currentIndex < baseStrTrimmed.length) {
        // Handle nested parenthesis
        if (baseStrTrimmed[currentIndex] === '(') {
            currentIndex = getParenthesisEnd(baseStrTrimmed, currentIndex);
            if (currentIndex === -1) throw new Error('Mismatched parenthesis');
        }
        // Handle quoted strings
        else if (baseStrTrimmed[currentIndex] === '"') {
            currentIndex = getQuoteEnd(baseStrTrimmed, currentIndex);
            if (currentIndex === -1) throw new Error('Mismatched quotes');
        }

        if (currentIndex === -1) break;

        // Check for the separator match
        if (separatorRegex.test(baseStrTrimmed[currentIndex])) {
            splits.push(baseStrTrimmed.substring(startIndex, currentIndex));
            startIndex = currentIndex + 1;
        }

        currentIndex++;
    }

    // Add the last segment if it exists
    if (startIndex < baseStrTrimmed.length) {
        splits.push(baseStrTrimmed.substring(startIndex));
    }

    // Trim each split segment
    return splits.map(segment => segment.trim());
};

/**
 * Matches a string against a pattern with wildcard support.
 * 
 * @param pattern The pattern to match against, can contain * (any characters) and _ (single character)
 * @param str The string to match
 * @param floating Whether to allow the pattern to match anywhere in the string (true) or only the entire string (false)
 * @returns True if the pattern matches the string, false otherwise
 */
export const wildcard_match_str = (pattern: string, str: string, floating: boolean=true): boolean => {
    // Escape special characters (leaving only `_` and `*` as meaningful)
    let escapedPattern = pattern.replace(/[-/\\^$+?.()|[\]{}]/g, '\\$&');
    // Replace `_` with `.` (single character wildcard)
    escapedPattern = escapedPattern.replace(/_/g, '.');
    // Replace `*` with `.*` (multiple character wildcard)
    escapedPattern = escapedPattern.replace(/\*/g, '.*');
    // Create a regular expression from the escaped pattern
    const regexPattern = floating ? new RegExp(escapedPattern) : new RegExp(`^${escapedPattern}$`);
    // Test the string against the regex
    return regexPattern.test(str);
}

/**
 * Converts a calculation result to a boolean value.
 * 
 * @param row The data row
 * @param calc The calculation function
 * @returns The boolean result
 */
export const calc_to_bool = (
    row: DATA_ROW,
    calc: (row: DATA_ROW) => CALC_RESULT,
): boolean => {
    const res = calc(row);
    switch (typeof res) {
        case 'string':
            return wildcard_match_str(res.toLowerCase(), row._raw.toLowerCase());
        case 'boolean':
            return res;
        case 'number':
        default:
            return !!res
    }
}

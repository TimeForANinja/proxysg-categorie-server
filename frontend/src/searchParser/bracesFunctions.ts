import { CALC_RESULT } from './types';

/**
 * The Structure used to store a braces-based function
 * e.g. "sin(2 + 2)"
 * This also gets used for generic braces () where the function name is "".
 */
export type BracesFunc = {
    // A prefix in front of the braces to mark a specific function
    key: string;
    // The method used to resolve the function from the value(s) inside
    calc: (...args: CALC_RESULT[]) => CALC_RESULT;
    // Validation function to check if the arguments are valid for the function
    validate: (argCount: number) => boolean;
}

/**
 * List of all known Braces Functions
 */
export const bracesFunctions: BracesFunc[] = [
    {
        key: 'abs',
        validate: (argCount: number): boolean => argCount === 1,
        calc: (...args: CALC_RESULT[]): number => Math.abs(Number(args[0])),
    },
    {
        key: '',
        validate: (argCount: number): boolean => argCount === 1,
        calc: (...args: CALC_RESULT[]): CALC_RESULT => args[0],
    },
];

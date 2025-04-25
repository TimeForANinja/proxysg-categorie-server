import { CALC_RESULT } from './types';

/**
 * The Structure used to store a braces-based function
 * e.g. "sin(2 + 2)"
 * This also gets used for generic braces () where the function name is "".
 */
export type BracesFunc = {
    // A prefix in front of the braces to mark a specific function
    key: string;
    // A description of the function, used in the UI
    description: string;
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
        description: 'calc the absolute value of the argument',
        validate: (argCount: number): boolean => argCount === 1,
        calc: (...args: CALC_RESULT[]): number => Math.abs(Number(args[0])),
    },
    {
        key: 'num',
        description: 'typecast string to a number',
        validate: (argCount: number): boolean => argCount === 1,
        calc: (...args: CALC_RESULT[]): number => Number(args[0]),
    },
    {
        key: '',
        description: 'simple braces to prioritise segments',
        validate: (argCount: number): boolean => argCount === 1,
        calc: (...args: CALC_RESULT[]): CALC_RESULT => args[0],
    },
];

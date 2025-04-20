/**
 * This file is the main entry point for the search parser.
 * It re-exports all the necessary components from the other files.
 */

import { ROOT_TYPE } from './argTypes';
import { TreeNode } from './treeNode';

// Re-export types
export type { CALC_RESULT, DATA_ROW } from './types';
export type { BracesFunc } from './bracesFunctions'
export type { ArgType } from './argTypes'

// Re-export utility functions
export {
    normalize,
    getQuoteEnd,
    getParenthesisEnd,
    splitArgs,
    wildcard_match_str,
    calc_to_bool,
    FUNC_ARG_SEPARATOR
} from './utils';

// Re-export argument types
export { bracesFunctions } from './bracesFunctions'
export { ROOT_TYPE, ARG_TYPES } from './argTypes';

// Re-export TreeNode class
export { TreeNode } from './treeNode';

/**
 * Build a new Tree, ready to be calculated
 *
 * @param baseStr the calculation
 * @returns the Root-TreeNode
 */
export const BuildSyntaxTree = (baseStr: string): TreeNode => {
    return new TreeNode(baseStr, ROOT_TYPE);
};

/**
 * This file is the main entry point for the search parser.
 * It re-exports all the necessary parts from the other files.
 */

import { ROOT_TYPE } from './argTypes';
import { TreeNode } from './treeNode';
import type { SearchParser} from "./treeNode";

// Re-export types
export type { DATA_ROW } from './types';
export type { BracesFunc } from './bracesFunctions'
export type { SearchParser } from './treeNode'

// Re-export argument types
export { bracesFunctions } from './bracesFunctions'


/**
 * Build a new Tree, ready to be calculated
 *
 * @param baseStr the calculation
 * @returns the Root-TreeNode
 */
export const BuildSyntaxTree = (baseStr: string): SearchParser => {
    return new TreeNode(baseStr, ROOT_TYPE);
};

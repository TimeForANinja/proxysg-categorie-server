/**
 * This file is the main entry point for the search parser.
 * It re-exports all the necessary parts from the other files.
 */

import { ROOT_TYPE } from './argTypes';
import { TreeNode } from './treeNode';
import type { SearchParser} from "./treeNode";
import {FieldDefinition} from "./fieldDefinition";

// Re-export types
export type { DATA_ROW } from './types';
export type { BracesFunc } from './bracesFunctions'
export type { SearchParser } from './treeNode'

// Re-export argument types
export { bracesFunctions } from './bracesFunctions'


/**
 * Build a new Tree, ready to be used for calculations
 *
 * @param baseStr the calculation
 * @param fields the list of fields available for use in calculation
 * @returns the Root-TreeNode
 */
export const BuildSyntaxTree = (
    baseStr: string,
    fields: FieldDefinition[]
): SearchParser => {
    const tree = new TreeNode(baseStr, ROOT_TYPE, fields);
    // call build on the root node to (try to) compile the try
    tree._buildHierarchy();
    return tree;
};

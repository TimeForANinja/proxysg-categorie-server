/**
 * This file contains the TreeNode class for the search parser.
 */

import {DATA_ROW, CALC_RESULT} from './types';
import {ARG_TYPES, ArgType} from "./argTypes";
import {calc_to_bool} from './utils';

/**
 * Simplified version of the TreeNode for external use
 */
export type SearchParser = {
    print(): string;
    test(row: DATA_ROW): boolean;
}

/**
 * A TreeNode is a Node in the Custom Language Tree used to calculate the values
 */
export class TreeNode implements SearchParser {
    /**
     * The original string that was parsed to create this TreeNode.
     */
    baseStr: string;
    /**
     * An array of TreeNode objects representing larger, nested Syntax Structures.
     */
    children: TreeNode[] = [];
    /**
     * Storage for Variables required for the ArgType
     * Allows to reuse values instead of calculating them multiple times (init, matches, print, calc...)
     */
    parts: string[] = [];
    /**
     * The ArgType of this TreeNode
     */
    type: ArgType;

    constructor(baseStr: string, type: ArgType) {
        this.baseStr = baseStr;
        this.type = type;

        // Parse baseStr and allow for children and parts to be populated
        this.type.init(this);
    }

    /**
     * variable to track if "nest()" has been called
     * nesting should only be done once
     */
    has_nested: boolean = false;

    /**
     * Nest required parts from the "all" TreeNodes under the current TreeNode.
     * This is done by calling the _nest function of the ArgType.
     *
     * @return {TreeNode[]} - The new array of all TreeNodes with updated nesting
     *
     * @param all
     */
    nest(all: TreeNode[]): TreeNode[] {
        this.has_nested = true;
        return this.type._nest(this, all);
    }

    /**
     * Builds a hierarchical structure from the children elements.
     * Iterates through each child element and applies a nesting operation
     * this allows for modifying the list of children by putting them "under" another child of the array.
     *
     * (e.g. changing [A, OR, B] to [OR(A, B)])
     *
     * @return {void}
     */
    _buildHierarchy(): void {
        while (true) {
            // only visit children once - this also does a shadow copy to not screw up the original array with the sort
            const todo = this.children.filter(x => !x.has_nested);
            // sort based on priority - the earlier in the ARG_TYPES array the higher the priority
            const sortByPriority = todo.sort((a, b) => ARG_TYPES.findIndex(x => x.name === a.type.name) - ARG_TYPES.findIndex(x => x.name === b.type.name));
            // (try to) pop the next child to visit, which is the one with the highest priority
            const child = sortByPriority[0];
            if (child === undefined) break;
            // call "nest" to handle moving arguments left and right of the "child" keyword
            // to within the "child" node
            this.children = child.nest(this.children);
        }

        // recursively call _buildHierarchy on all children
        for (const child of this.children) {
            child._buildHierarchy();
        }
    }

    print(): string {
        return this.type.print(this);
    }

    /**
     * Calculates the value of this TreeNode.
     * This is done by recursively calling the _calc function of the children.
     * The result of the calculation is then returned.
     *
     * This differs from the test function in that it does not convert the result to a boolean.
     * This is required since some calculations may return a string or number instead of a boolean.
     * Those strings are required to be kept intact for variables like key_value that can match against fields.
     *
     * @param row
     */
    _calc(row: DATA_ROW): CALC_RESULT {
        return this.type._calc(this, row);
    }

    /**
     * Tests if the value of this TreeNode is true for the given row.
     * This is done by recursively calling the _calc function of the children
     * and then converting the result to a boolean by matching it against the raw value of the row.
     *
     * @param row
     */
    test(row: DATA_ROW): boolean {
        return calc_to_bool(row, this._calc.bind(this));
    }
}

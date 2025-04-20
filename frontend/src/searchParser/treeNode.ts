/**
 * This file contains the TreeNode class for the search parser.
 */

import { DATA_ROW, CALC_RESULT,  } from './types';
import { ArgType } from "./argTypes";
import { calc_to_bool } from './utils';

/**
 * A TreeNode is a Node in the Custom Language Tree used to calculate the values
 */
export class TreeNode {
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

        // Parse TXT based on Child
        this.type.init(this);

        // try to adjust the hierarchy (e.g. changing [A, OR, B] to [OR(A, B)])
        this.buildHierarchy();
    }

    /**
     * Builds a hierarchical structure from the children elements.
     * Iterates through each child element, applying a nesting operation
     * that may modify the list of children by putting them "under" another child of the array.
     * @return {void}
     */
    private buildHierarchy(): void {
        let idx = 0;
        while (idx < this.children.length - 1) {
            const child = this.children[idx];

            this.children = child.type.nest(child, this.children);
            // some weird trickery
            // since .nest can remove items from this.children we need to recalculate where we're at
            // or rather what's the next idx to check
            idx = this.children.indexOf(child) + 1;
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
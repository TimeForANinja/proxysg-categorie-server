import {CALC_RESULT, DATA_ROW} from './types';
import { FUNC_ARG_SEPARATOR, calc_to_bool, normalize, splitArgs, wildcard_match_str } from './utils';
import { TreeNode } from './treeNode'
import { bracesFunctions } from './bracesFunctions';

/**
 * ArgType represents any recognised syntax expression of a parseable search query
 */
export type ArgType = {
    /**
     * A name to reference this by
     */
    name: string;
    /**
     * Function to determine if the argument type matches a given string.
     * The strings are always individual arguments, so split by (" " and "," depending on context)
     *
     * @param baseStr - The input string to match against.
     * @returns {boolean} - Returns true if the type matches the string, otherwise false.
     */
    matches: (baseStr: string) => boolean;
    /**
     * Function to initialize the argument type.
     * This mainly populates the "children" and "parts" Property of the TreeNode
     *
     * @param self - The TreeNode instance to initialize.
     */
    init?: (self: TreeNode) => void;
    /**
     * Function to nest the argument type within other TreeNodes.
     *
     * this allows to transform e.g. [A, OR, C] into a nested [OR(A, B)]
     * by moving arguments from a higher level to the children level of the current (self) instance
     *
     * @param self - The TreeNode instance to nest.
     * @param all - An array of TreeNode instances of the next higher level.
     * @returns {TreeNode[]} - The nested array of TreeNode instances.
     */
    _nest?: (self: TreeNode, all: TreeNode[]) => TreeNode[];
    /**
     * Function to print the argument type for debugging.
     *
     * @param self - The TreeNode instance to print.
     * @returns {string} - The string representation of the TreeNode.
     */
    print: (self: TreeNode) => string;
    /**
     * Function to calculate the value of the argument type.
     *
     * @param self - The TreeNode instance to calculate.
     * @param row - The row of the data to calculate the value for.
     * @returns {string} - The string representation of the calculated value.
     */
    _calc: (self: TreeNode, row: DATA_ROW) => CALC_RESULT;
};

/**
 * The root argument type, which is the entry point for parsing.
 */
export const ROOT_TYPE: ArgType = {
    name: 'root',
    matches: () => false,
    init: self => {
        // normalize inputs of ROOT-Nodes
        self.baseStr = normalize(self.baseStr);

        // split into args on spaces
        const arg_strings = splitArgs(self.baseStr, " ");

        // for each part, try to identify the arg type and append as children
        for (const arg of arg_strings) {
            const type = ARG_TYPES.find(at => at.matches(arg));
            if (type) {
                self.children.push(new TreeNode(arg, type, self.fields));
            } else {
                throw new Error(`Unable to find a Type for "${arg}"`)
            }
        }
    },
    print: self => `root([${self.children.map(c => c.print()).join(', ')}])`,
    _calc: (self, row) => {
        if (self.children.length === 1) {
            return self.children[0]._calc(row);
        }
        // Start with value "true" and "stack" results for all children
        return self.children.reduce<boolean>((current, child) => {
            return current && calc_to_bool(row, child._calc.bind(child));
        }, true);
    }
}

/**
 * All supported argument types for the parser.
 */
export const ARG_TYPES: ArgType[] = [
    ROOT_TYPE,
    {
        name: 'empty',
        matches: str => str.length === 0,
        print: () => `null()`,
        _calc: (_self, _row): string => "",
    },
    {
        name: 'not',
        matches: str => str === 'NOT',
        _nest: (self, all) => {
            const idx = all.indexOf(self);
            // Remove the next element from the "all" array and add it as a child to this NOT element
            const next = all.splice(idx+1, 1)[0];
            if (next === undefined) {
                throw new Error(`NOT at the end is not allowed`)
            }
            // no typecast required, since they are already TreeNode's
            self.children = [next];
            return all;
        },
        print: self => `not([${self.children.map(c => c.print()).join(', ')}])`,
        _calc: (self, row): boolean => {
            // Invert the result of the child
            return !calc_to_bool(row, self.children[0]._calc.bind(self.children[0]));
        },
    },
    {
        name: 'logic',
        matches: str => ['OR', 'AND'].includes(str),
        _nest: (self, all) => {
            const idx = all.indexOf(self);
            // remove the next and prev element from the "all" array since they are combined by this logic
            // add the parts as children under this logic element
            const next = all.splice(idx+1, 1)[0];
            const prev = all.splice(idx-1, 1)[0];
            // no typecast required, since they are already TreeNode's
            self.children = [prev, next];
            return all;
        },
        print: self => `logic(${self.baseStr}, [${self.children.map(c => c.print()).join(', ')}])`,
        _calc: (self, row): boolean => {
            if (self.baseStr === 'OR') {
                return self.children.reduce<boolean>((current, child): boolean => {
                    return current || calc_to_bool(row, child._calc.bind(child));
                }, false)
            } else {
                return self.children.reduce<boolean>((current, child): boolean => {
                    return current && calc_to_bool(row, child._calc.bind(child));
                }, true)
            }
        },
    },
    {
        name: 'key-val-pair',
        matches: str => {
            const args = splitArgs(str, "=");
            return args.length === 2;
        },
        init: self => {
            const args = splitArgs(self.baseStr, "=");
            // split into (key, operation, val) using a regex
            // store all of them inside parts
            self.parts = [
                args[0], "=", args[1],
            ];
            // then create children based on the "val" part
            self.children = [new TreeNode(self.parts[0], ROOT_TYPE, self.fields), new TreeNode(self.parts[2], ROOT_TYPE, self.fields)];
        },
        print: self => `key-val(${self.children[0].print()}, ${self.children[1].print()})`,
        _calc: (self, row) => {
            return wildcard_match_str(
                self.children[1]._calc(row).toString().toLowerCase(),
                self.children[0]._calc(row).toString().toLowerCase(),
                false
            )
        },
    },
    {
        name: 'bracesFunc',
        matches:str => str.endsWith(")") && bracesFunctions.some(bf => str.startsWith(bf.key + '(')),
        init: self => {
            // find func by name and store in parts
            const func_name = bracesFunctions.find(bf => self.baseStr.startsWith(bf.key + '('))!
            self.parts = [func_name.key];

            // then build "args" and later "children" from the stuff inside the func brackets
            const raw_inner = self.baseStr.substring(func_name.key.length + 1, self.baseStr.length - 1);
            const inner = splitArgs(raw_inner, FUNC_ARG_SEPARATOR);
            if (!func_name.validate(inner.length)) {
                throw new Error(`Invalid arguments for function "${func_name.key}"`)
            }
            self.children = inner.map(i => new TreeNode(i, ROOT_TYPE, self.fields));
        },
        print: self => `func(${self.parts[0]}, [${self.children.map(c => c.print()).join(', ')}])`,
        _calc: (self, row) => {
            const func = bracesFunctions.find(bf => bf.key === self.parts[0])!
            return func.calc(...self.children.map(c => c._calc(row)));
        },
    },
    {
        name: 'quoted-text',
        matches: str => str.startsWith('"') && str.endsWith('"'),
        init: self => {
            self.parts = [self.baseStr.substring(1, self.baseStr.length - 1)];
        },
        print: self => `text("${self.parts[0]}")`,
        _calc: (self, _row): string => {
            return self.parts[0];
        },
    },
    {
        name: 'raw-text',
        matches: str => /^\S+$/.test(str),
        print: self => `text_or_column("${self.baseStr}")`,
        _calc: (self, row) => {
            if (row.hasOwnProperty(self.baseStr)) {
                return row[self.baseStr]
            }
            return self.baseStr;
        },
    },
];

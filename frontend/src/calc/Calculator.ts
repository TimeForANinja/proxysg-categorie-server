/**
 * This file contains various utilities and definitions for handling and processing mathematical
 * expressions embedded within strings. It includes constants, types, functions, and classes aimed
 * at parsing, normalizing, and evaluating such expressions with proper handling of nested structures
 * and quoted sections.
 *
 * Here are the main components defined in this file:
 *
 * Constants:
 * - `FUNC_ARG_SEPERATOR`: A comma used to separate function arguments in strings.
 *
 * Types:
 * - `BracesFunc`: Represents a function that is enclosed within braces, such as "sin(2 + 2)".
 *
 * Functions:
 * - `normalize(baseStr: string)`: Normalizes a string by trimming and adjusting spaces while preserving quoted content.
 * - `getQuoteEnd(baseStr: string, startIDX: number)`: Finds the end of a quoted section in a string.
 * - `getParenthesisEnd(baseStr: string, startIDX: number)`: Finds the end of a parenthesized section in a string.
 * - `splitArgs(baseStr: string, separator: string)`: Splits a string into arguments based on a specified separator while handling nested braces and quotes.
 *
 * Classes:
 * - `TreeNode`: Represents a node in a custom language tree used for parsing and calculating expressions.
 *
 * Types:
 * - `OperandChild`: A union type representing a child node, which can be either a string or another `TreeNode`.
 * - `Operand`: Defines an interaction between multiple parameters, including methods to match and calculate expressions.
 *
 * Constants:
 * - `OPERANTS`: A list of all known operands that can be used in expressions, each with methods to match, get children, and calculate the result of the operand.
 */

/**
 * The Character splitting Function Parameters
 */
const FUNC_ARG_SEPARATOR = Object.freeze(',');
/**
 * The Structure used to store a braces-based function
 * e.g. "sin(2 + 2)"
 * This also gets used for generic braces () where the function name is "".
 */
type BracesFunc = {
  // A prefix in front of the braces to mark a specific function
  key: string;
  // The method used to resolve the function from the value(s) inside
  calc: (...args: string[]) => string;
}
/**
 * List of all known Braces Functions
 */
const bracesFunctions: BracesFunc[] = [
  { key: 'abs', calc: (n: string): string => Math.abs(Number(n)).toString() },
  { key: '', calc: (n: string): string => n },
];

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
    if (escaped[i] == "\"") {
      const end = getQuoteEnd(escaped, i)
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
      console.log("escaped", end, baseStr[end]);
      // Skip the next character
      end++;
      continue;
    }

    if (baseStr[end] === "\"") {
      console.log("string", end, baseStr[end]);
      // skip to end of string
      end = getQuoteEnd(baseStr, end);
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
    // Handle nested parentheses
    if (baseStrTrimmed[currentIndex] === '(') {
      currentIndex = getParenthesisEnd(baseStrTrimmed, currentIndex);
      if (currentIndex === -1) throw new Error('Mismatched parentheses');
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
 * ArgType represents any recognised syntax expression of a parseable search query
 */
type ArgType = {
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
  init: (self: TreeNode) => void;
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
  nest: (self: TreeNode, all: TreeNode[]) => TreeNode[];
  /**
   * Function to print the argument type for debugging.
   *
   * @param self - The TreeNode instance to print.
   * @returns {string} - The string representation of the TreeNode.
   */
  print: (self: TreeNode) => string;
};
const ROOT_TYPE: ArgType = {
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
        self.children.push(new TreeNode(arg, type));
      } else {
        throw new Error(`Unable to find a Type for "${arg}"`)
      }
    }
  },
  nest: (_, all) => all,
  print: self => `root([${self.children.map(c => c.print()).join(', ')}])`,
}
const ARG_TYPES: ArgType[] = [
  ROOT_TYPE,
  {
    name: 'empty',
    matches: str => str.length === 0,
    init: () => null,
    nest: (_, all) => all,
    print: () => `null()`,
  },
  {
    name: 'logic',
    matches: str => ['OR', 'AND'].includes(str),
    init: () => null,
    nest: (self, all) => {
      const idx = all.indexOf(self);
      // remove the next and prev element from the "all" array since they are combined bis this logic
      // add the parts as children under this logic element
      const next = all.splice(idx+1, 1)[0];
      const prev = all.splice(idx-1, 1)[0];
      // no typecast required, since they are already TreeNode's
      self.children = [prev, next];
      return all;
    },
    print: self => `logic(${self.baseStr}, [${self.children.map(c => c.print()).join(', ')}])`,
  },
  {
    name: 'key-val-pair',
    matches: str => /^([^ \n]+)([=><])([^ \n]+)$/.test(str),
    init: self => {
      // split into (key, operation, val) using a regex
      // store all of them inside parts
      self.parts = [
          ...self.baseStr.match(/^([^ \n]+)([=><])([^ \n]+)$/)!,
      ];
      // then create children based of the "val" part
      self.children = [new TreeNode(self.parts[3], ROOT_TYPE)];
    },
    nest: (_, all)  => all,
    print: self => `key-val("${self.parts[1]}", ${self.children[0].print()})`,
  },
  {
    name: 'bracesFunc',
    matches:str => str.endsWith(")") && bracesFunctions.some(bf => str.startsWith(bf.key + '(')),
    init: self => {
      // find func by name and store in parts
      const func_name = bracesFunctions.find(bf => self.baseStr.startsWith(bf.key + '('))!.key
      self.parts = [func_name];

      // then build "args" and later "children" from the stuff inside the func brackets
      const raw_inner = self.baseStr.substring(func_name.length + 1, self.baseStr.length - 1);
      const inner = splitArgs(raw_inner, FUNC_ARG_SEPARATOR);
      self.children = inner.map(i => new TreeNode(i, ROOT_TYPE));
    },
    nest: (_, all) => all,
    print: self => `func(${self.parts[0]}, [${self.children.map(c => c.print()).join(', ')}])`,
  },
  {
    name: 'quoted-text',
    matches: str => str.startsWith('"') && str.endsWith('"'),
    init: self => {
      self.parts = [
        self.baseStr.substring(1, self.baseStr.length - 1)
      ];
    },
    nest: (_, all) => all,
    print: self => `text("${self.parts[0]}")`,
  },
  {
    name: 'raw-text',
    init: () => null,
    matches: str => /^\S+$/.test(str),
    nest: (_, all) => all,
    print: self => `text("${self.baseStr}")`,
  },
];

/**
 * A TreeNode is a Node in the Custom Language Tree used to calculate the values
 */
class TreeNode {
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
      console.log(`buildHierarchy(${idx}, ${this.children.length})`, child.baseStr, '->', '[', this.children.map(a => a.baseStr).join(', '), ']');

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
}

/**
 * Build a new Tree, ready to be calculated
 *
 * @param baseStr the calculation
 * @returns the Root-TreeNode
 */
export const BuildSyntaxTree = (baseStr: string): TreeNode => {
  return new TreeNode(baseStr, ROOT_TYPE);
};

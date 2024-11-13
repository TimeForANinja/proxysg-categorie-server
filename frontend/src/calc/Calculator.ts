// The Character splitting Function Parameters
const ARG_SEPERATOR = Object.freeze(',');

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
// List of all known Braces Functions
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

// --------------------------------------------------------------------------------

/**
 * Cut the inside of braces into arguments based on ARG_SEPERATOR.
 *
 * Allows for another nested braces func with multiple arguments
 * by using the same stack-approach as getEnd().
 *
 * @param baseStr the string inside the braces
 * @returns an array of arguments
 */
const getArgs = (baseStr: string): string[] => {
  let splitStart = 0;
  const splits = [];
  let stack = 0;
  for (let i = 0 ; i < baseStr.length; i++) {
    // update stack
    if (baseStr[i] === '(') {stack++;}
    else if (baseStr[i] === ')') {stack--;}
    // cut args
    if (stack === 0 && baseStr[i] === ARG_SEPERATOR) {
      splits.push(baseStr.substring(splitStart, i));
      splitStart = i + 1;
    }
  }
  // one last arg has to be cut manually
  splits.push(baseStr.substring(splitStart));
  return splits;
};

type OperandChild = TreeNode | string;
/**
 * Operand is an interaction between one / multiple parameters
 */
type Operand = {
  // Name for debugging purpose
  name: string;
  // Returns true if a string requires the Operator to be applied
  matches: (baseStr: string) => boolean;
  getChildren: (baseStr: string) => OperandChild[];
  calc: (children: OperandChild[]) => string;
}
// Definition aller bekannten Operanden
const OPERANTS: Operand[] = [
  {
    name: 'empty',
    matches: (baseStr) => baseStr.length === 0,
    getChildren: () => [],
    calc: () => "",
  },
  {
    name: "or",
    matches: (baseStr) => baseStr.includes("OR"),
    getChildren: () => [],
    calc: () => "",
  },
  {
    name: 'bracesFunc',
    matches: (baseStr) => bracesFunctions.some(bf => baseStr.includes(bf.key + '(') && getParenthesisEnd(baseStr, bf.key.length) >= 0),
    getChildren: (baseStr) => {
      const braceFunc = bracesFunctions.find(bf => baseStr.includes(bf.key + '(') && getParenthesisEnd(baseStr, bf.key.length) >= 0)!;
      const func_start = baseStr.indexOf(braceFunc.key + "(");
      const func_end = baseStr.indexOf(")", func_start);

      return [
          new TreeNode(baseStr.substring(0, func_start)),
          braceFunc.key,
          new TreeNode(baseStr.substring(func_start +1, func_end)),
          new TreeNode(baseStr.substring(func_end +2)),
      ];
      /*
      // Check if any of the Braces-Functions does apply
      for (const bf of bracesFunctions) {
        if (baseStr.includes(bf.key + '(')) {
          const end = getEnd(baseStr, bf.key, "(", ")");
          // The end should be after the start
          if (end >= 0) {
            const start = baseStr.indexOf(bf.key + '(');
            // save subterm & return newly composed string
            const id = `s${subterms.size}`;
            subterms.set(id, { type: bf.key, substrings: getArgs(baseStr.substring(start + 1 + bf.key.length, end)) });
            return [baseStr.substr(0, start) + id + baseStr.substr(end + 1)];
          }
        }
      }
      throw new Error('how did you get here?');
       */
    },
    calc: (children) => `(${(children[0] as TreeNode).calc()}) AND func("${children[1]}", "${(children[2] as TreeNode).calc()}") AND (${(children[3] as TreeNode).calc()})`,
  },
  {
    name: 'key-val-pair',
    matches: str => /(.*\s|^)([^ \n]+)([=><])([^ \n]+)(\s.*|$)/.test(str),
    getChildren: (baseStr) => {
      const match = baseStr.match(/((.*)\s|^)([^ \n]+)([=><])([^ \n]+)(\s(.*)|$)/)!
      return [
        new TreeNode(match[2] || ""),
        match[3],
        new TreeNode(match[5]),
        new TreeNode(match[7] || ""),
      ]
    },
    calc: (children) => `(${(children[0] as TreeNode).calc()}) AND keyval("${children[1]}", "${(children[2] as TreeNode).calc()}") AND (${(children[3] as TreeNode).calc()})`,
  },
  {
    name: 'quoted-text',
    matches: str => /^"([^"\\]+\\(\\\\)*")*[^"]*"$/.test(str),
    getChildren: (baseStr) => [baseStr.substring(1, baseStr.length - 1)],
    calc: (children) => `txt("${children[0]}")`,
  },
  {
    name: 'raw-text',
    matches: str => /(\s|^)\S+(\s|$)/.test(str),
    getChildren: (baseStr) => [baseStr],
    calc: (children) => `txt("${children[0]}")`,
  },
];

/**
 * A TreeNode is a Node in the Custom Language Tree used to calculate the values
 */
export class TreeNode {
  baseStr: string;
  children: OperandChild[] = [];
  operand: Operand | null = null;

  constructor(baseStr: string) {
    console.log('new TreeNode()', { baseStr });
    this.baseStr = baseStr;
    this.build();
  }

  /**
   * Build a new Tree, ready to be calculated
   *
   * @param baseStr the calculation
   * @returns the Root-TreeNode
   */
  static buildTree(baseStr: string): TreeNode {
    // normalize first input
    const norm = normalize(baseStr);
    return new TreeNode(norm);
  }

  /**
   * Recursively build the Tree structure
   *
   * @returns
   */
  private build(): void {
    for (const op of OPERANTS) {
      const testOP = op.matches(this.baseStr);
      console.log('TreeNode#build', { name: op.name, testOP });
      if (testOP) {
        this.operand = op;
        this.children = op.getChildren(this.baseStr);
        return;
      }
    }
    // throw new Error('invalid expression');
  }

  calc(): string {
    return this.operand ? this.operand.calc(this.children) : "INVALID";
  }
}

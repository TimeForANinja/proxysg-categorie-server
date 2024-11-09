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
 * Get the closing bracket or character to match an opening one.
 *
 * Uses a stack-based algorithm to track opening and closing characters,
 * allowing for nested braces, brackets, and quotes.
 *
 * @param baseStr The input string.
 * @param prefix The prefix before the opening character.
 * @param openChar The opening character to track (e.g., '(', '[', '{', or '"').
 * @param closeChar The closing character to track (e.g., ')', ']', '}', or '"').
 * @returns The index of the closing character or -1 if not found.
 */
const getEnd = (baseStr: string, prefix: string, openChar: string, closeChar: string): number => {
  const start = baseStr.indexOf(prefix + openChar) + prefix.length;
  let stack = 1;
  let end = start;
  while (++end < baseStr.length) {
    // Skip escaped characters (e.g., \")
    if (baseStr[end] === '\\' && baseStr[end + 1] === closeChar) {
      end++; // Skip the next character
      continue;
    }
    // Update stack for nested structures
    if (baseStr[end] === openChar) {
      stack++;
    } else if (baseStr[end] === closeChar) {
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

/**
 * The Subterm class is used to replace brace-Functions
 * The type is the braces prefix - later required to calculate the value of the braces-Function
 * the substring is the string part inside the braces
 */
type Subterm = {
  type: string;
  substrings: string[];
}

/**
 * Operand is an interaction between one / multiple parameters
 */
type Operand = {
  // Name for debugging purpose
  name: string;
  // Returns true if a string requires the Operator to be applied
  matches: (baseStr: string) => boolean;
  // Returns a List of subterms to be evaluated recursively
  getChildren: (baseStr: string, subterms: Map<string, Subterm>) => string[];
}
// Definition aller bekannten Operanden
const OPERANTS: Operand[] = [
  {
    name: 'bracesFunc',
    matches: (baseStr) => bracesFunctions.some(bf => baseStr.includes(bf.key + '(') && getEnd(baseStr, bf.key, "(", ")") >= 0),
    getChildren: (baseStr, subterms) => {
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
    },
  },
  {
    name: 'key-val-pair',
    matches: str => /(\s|^)([^ \n]+)\s*([=><])\s*([^ \n]+)(\s|$)/.test(str),
    getChildren: (baseStr) => [
      baseStr.match(/(\s|^)([^ \n]+)\s*([=><])\s*([^ \n]+)(\s|$)/)![4],
    ],
  },
  {
    name: 'quoted-text',
    matches: str => /^"([^"\\]+\\(\\\\)*")*[^"]*"$/.test(str),
    getChildren: () => [],
  },
  {
    name: 'raw-text',
    matches: str => /(\s|^)\S+(\s|$)/.test(str),
    getChildren: () => [],
  },
];

/**
 * A TreeNode is a Node in the Custom Language Tree used to calculate the values
 */
export class TreeNode {
  baseStr: string;
  childs: TreeNode[];
  operand: Operand | null;
  // Subterms is a map allowing for replacements that are later evaluated as Operand
  // This makes stuff like Braces way easier
  subterms: Map<string, Subterm>;

  private constructor(baseStr: string, subterms: Map<string, Subterm> = new Map()) {
    console.log('new TreeNode', { baseStr, subterms });
    this.baseStr = baseStr;
    this.childs = [];
    this.operand = null;
    this.subterms = subterms;

    this.build();
  }

  /**
   * Build a new Tree, ready to be calculated
   *
   * @param baseStr the calculation
   * @returns the Root-TreeNode
   */
  static buildTree(baseStr: string): TreeNode {
    // remove multiple whitespaces
    baseStr = baseStr.toLowerCase().replace(/\s+/g, ' ')
    return new TreeNode(baseStr);
  }

  /**
   * Recursively build the Tree structure
   *
   * @returns
   */
  private build(): void {
    for (const op of OPERANTS) {
      const testOP = op.matches(this.baseStr);
      console.log("build", op.name, testOP);
      if (testOP) {
        this.operand = op;
        const childStrs = op.getChildren(this.baseStr, this.subterms);
        this.childs = childStrs.map(str => new TreeNode(str, this.subterms));
        return;
      }
    }
    throw new Error('invalid expression');
  }
}

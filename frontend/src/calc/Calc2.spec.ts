import { TreeNode } from './Calculator';

type TestObject = {
  description: string;
  in: string;
  out: number;
};
const testStrings: TestObject[] = [
  { description: 'only text', in: 'asdf', out: 2 },
  { description: 'key-val-pair', in: 'key=val', out: 5 },
  { description: 'key-val-pair with spaces', in: 'key = val', out: 5 },
  /*
{ description: 'mixed use of text and key = Val', in: 'asdf key = val', out: 14 },

{ description: 'mixed use of text and key = Val', in: 'key = val asdf', out: 14 },
{ description: 'handles braces', in: '(asdf) key = val', out: 20 },
{ description: 'handles quotes', in: '"asdf yey"', out: 10 },
{ description: 'handles qoted and key=val', in: '"asdf yey" OR key = val', out: 10 },
{ description: 'handles AND and OR', in: 'a AND b OR c', out: 3 },
*/
];

describe('Does Something', () => {
  for (const test of testStrings) {
    it(test.description, () => {
      const calc = TreeNode.buildTree(test.in);
      console.log(calc);
    });
  }

});

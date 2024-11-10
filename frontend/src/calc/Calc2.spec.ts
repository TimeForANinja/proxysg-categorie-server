import { TreeNode, normalize } from './Calculator';

type TestParserObject = {
  description: string;
  in: string;
  out: number;
};
const parserTests: TestParserObject[] = [
{ description: 'only text', in: 'asdf', out: 2 },
{ description: 'key-val-pair', in: 'key=val', out: 5 },
{ description: 'key-val-pair with spaces', in: 'key = val', out: 5 },
{ description: 'mixed use of text and key = Val', in: 'asdf key = val', out: 14 },
{ description: 'mixed use of text and key = Val', in: 'key = val asdf', out: 14 },
{ description: 'handles braces', in: '(asdf) key = val', out: 20 },
{ description: 'handles quotes', in: '"asdf yey"', out: 10 },
{ description: 'handles qoted and key=val', in: '"asdf yey" OR key = val', out: 10 },
{ description: 'handles AND and OR', in: 'a AND b OR c', out: 3 },
];

describe('Parser', () => {
  for (const test of parserTests) {
    it(test.description, () => {
      const calc = TreeNode.buildTree(test.in);
      console.log(calc);
    });
  }
});

type TestNormalizeObject = {
  description: string;
  in: string;
  out: string;
}
const normalizationTests: TestNormalizeObject[] = [
  { description: "Nothing to normalize", in: "asdf", out: "asdf"},
  { description: "Removes trailing spaces", in: "  asdf  ", out: "asdf"},
  { description: "Replaces multiple spaces with single", in: "foo   bar", out: "foo bar"},
  { description: "Replaces tab with spaces", in: "foo\t\tbar", out: "foo bar"},
  { description: "Does not escape multi-spaces inside quotes", in: "foo\"  \"bar", out: "foo\"  \"bar"},
  { description: "Does not escape multi-spaces inside quotes\neven if they include \"escaped\" characters", in: "foo\"  \\\"  \"bar", out: "foo\"  \\\"  \"bar"},
  { description: "Does escape text between quoted text", in: "foo\"  \"bar  foo\"  \"bar", out: "foo\"  \"bar foo\"  \"bar"},
  { description: "Removes spaces around math operations =", in: "foo  a = b  bar", out: "foo a=b bar"},
  { description: "Removes spaces around math operations <", in: "foo  a < b  bar", out: "foo a<b bar"},
  { description: "Removes spaces around math operations >", in: "foo  a > b  bar", out: "foo a>b bar"},
  { description: "Does not remove spaces around math operation in quotes", in: "foo\"  yes = boy  \"bar", out: "foo\"  yes = boy  \"bar"},
]
describe('Normalize', () => {
  for (const test of normalizationTests) {
    it(test.description, () => {
      const result = normalize(test.in);
      expect(result).toBe(test.out);
    });
  }
});

import { TreeNode, normalize } from './Calculator';

type TestParserObject = {
  description: string;
  in: string;
  out: string;
};
const parserTests: TestParserObject[] = [
  { description: 'only text', in: 'asdf', out: 'txt("asdf")' },
  { description: 'key-val-pair', in: 'key=val', out: '() AND keyval("key", "txt("val")") AND ()' },
  { description: 'key-val-pair with spaces', in: 'key = val', out: '() AND keyval("key", "txt("val")") AND ()' },
  { description: 'mixed use of text and key = Val', in: 'asdf key = val', out: '(txt("asdf")) AND keyval("key", "txt("val")") AND ()' },
  { description: 'mixed use of text and key = Val', in: 'key = val asdf', out: '() AND keyval("key", "txt("val")") AND (txt("asdf"))' },
  { description: 'handles braces', in: '(asdf) key = val', out: '() AND func("", "txt("asdf")") AND (() AND keyval("key", "txt("val")") AND ())' },
  { description: 'handles quotes', in: '"asdf yey"', out: 'txt("asdf yey")' },
  { description: 'handles quoted and key=val', in: '"asdf yey" OR key = val', out: '' },
  { description: 'handles AND and OR', in: 'a AND b OR c', out: '' },
];

describe('Parser', () => {
  for (const test of parserTests) {
    it(test.description, () => {
      const tree = TreeNode.buildTree(test.in);
      const calc = tree.calc();
      expect(calc).toBe(test.out);
    });
  }
});

/*
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
*/

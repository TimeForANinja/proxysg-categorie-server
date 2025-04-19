import {
    normalize,
    getQuoteEnd,
    getParenthesisEnd,
    splitArgs,
    BuildSyntaxTree, wildcard_match_str,
} from './Parser';

type TestParserObject = {
    description: string;
    in: string;
    out: string;
};
const parserTests: TestParserObject[] = [
    { description: 'only text', in: 'asdf', out: 'root([text_or_column("asdf")])' },
    { description: 'key-val-pair', in: 'key=val', out: 'root([key-val(root([text_or_column("key")]), root([text_or_column("val")]))])' },
    { description: 'key-val-pair with spaces', in: 'key = val', out: 'root([key-val(root([text_or_column("key")]), root([text_or_column("val")]))])' },
    { description: 'mixed use of text and key = Val', in: 'asdf key = val', out: 'root([text_or_column("asdf"), key-val(root([text_or_column("key")]), root([text_or_column("val")]))])' },
    { description: 'mixed use of text and key = Val', in: 'key = val asdf', out: 'root([key-val(root([text_or_column("key")]), root([text_or_column("val")])), text_or_column("asdf")])' },
    { description: 'handles braces', in: '(asdf) key = val', out: 'root([func(, [root([text_or_column("asdf")])]), key-val(root([text_or_column("key")]), root([text_or_column("val")]))])' },
    { description: 'handles quotes', in: '"asdf yey"', out: 'root([text("asdf yey")])' },
    { description: 'handles quoted and key=val', in: '"asdf yey" key=val', out: 'root([text("asdf yey"), key-val(root([text_or_column("key")]), root([text_or_column("val")]))])' },
    { description: 'handles AND and OR', in: 'a AND b OR c', out: 'root([logic(OR, [logic(AND, [text_or_column("a"), text_or_column("b")]), text_or_column("c")])])' },
];
describe('Parser', () => {
    for (const test of parserTests) {
        it(test.description, () => {
            const tree = BuildSyntaxTree(test.in);
            const calc = tree.print();
            expect(calc).toBe(test.out);
        });
    }
});
const parserInvalidTests: TestParserObject[] = [
    { description: 'uneven quotes', in: 'as"df', out: 'Mismatched quotes' },
    { description: 'uneven parenthesis', in: 'as(df', out: 'Mismatched parenthesis' },
    { description: 'uneven parenthesis due to quotes', in: 'as("df)"', out: 'Mismatched parenthesis' },
];
describe('Parser - Invalid Input', () => {
    for (const test of parserInvalidTests) {
        it(test.description, () => {
            let error = "";
            try {
                BuildSyntaxTree(test.in);
            } catch (e: Error | any) {
                error = e?.message;
            }
            expect(error).toBe(test.out);
        });
    }
});

type TestParserCalcObject = {
    description: string;
    in: string;
    row: {[key: string]: string, _raw: string};
    out: boolean;
};
const parserCalcTests: TestParserCalcObject[] = [
    {description: 'simple string match', in: 'e', row: {_raw: "test"}, out: true},
    {description: 'key-val test 01', in: 'a = b', row: {_raw: "c", a: "b"}, out: true},
    {description: 'key-val test 02', in: 'a = bc', row: {_raw: "c", a: "b"}, out: false},
    {description: 'key-val test 03', in: 'a = bc', row: {_raw: "c", a: "bcd"}, out: false},
    {description: 'complex example 01', in: 'ab OR cd', row: {_raw: "acd"}, out: true},
    {description: 'key-val wildcard 01', in: 'a = *b', row: {_raw: "c", a: "ab"}, out: true},
    {description: 'key-val not matching raw', in: 'a=b', row: {_raw: "a=b", a: "c"}, out: false},
    {description: 'key-val complex 01', in: '3 = abs(-3)', row: {_raw: "abcd"}, out: true},
]
describe('Parser:calc', () => {
    for (const test of parserCalcTests) {
        it(test.description, () => {
            const tree = BuildSyntaxTree(test.in);
            const calc = tree.test(test.row);
            expect(calc).toBe(test.out);
        });
    }
})

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

type TestGetQuoteEndObject = {
    description: string;
    in: string;
    start: number;
    end: number;
}
const getQuoteEndTests: TestGetQuoteEndObject[] = [
    {
        description: "Should return the index of the ending quote for a simple string",
        in: 'This is a "test" string.',
        start: 10,
        end: 15
    },
    {
        description: "Should return the index of the ending quote for a string with escaped quote inside",
        in: 'This is a "test \\"escaped\\" quote" string.',
        start: 10,
        end: 33
    },
    {
        description: "Should handle multiple escaped backslashes",
        in: 'This is a "test string\\\\"escaped\\" string.',
        start: 10,
        end: 24
    },
    {
        description: "Should return -1 for an uninterrupted quote",
        in: 'This is a "test with no end',
        start: 10,
        end: -1
    },
    {
        description: "Should handle quotes next to each other",
        in: 'This is a ""test"" string.',
        start: 10,
        end: 11
    },
    {
        description: "Should handle single character string with quote",
        in: '"',
        start: 0,
        end: -1
    },
    {
        description: "Should return the correct ending index for nested quotes",
        in: 'This is a "nested \\"quote\\"" example',
        start: 10,
        end: 27
    },
    {
        description: "Should handle quotes at the beginning of the string",
        in: '"This is at the beginning"',
        start: 0,
        end: 25
    },
    {
        description: "Should handle multi-quote sections in string",
        in: '"First section" and "second section"',
        start: 0,
        end: 14
    },
]
describe("getQuoteEnd", () => {
    for (const test of getQuoteEndTests) {
        it(test.description, () => {
            const result = getQuoteEnd(test.in, test.start);
            expect(result).toBe(test.end);
        });
    }
})

type TestGetParenthesisEndObject = {
    description: string;
    in: string;
    start: number;
    end: number;
}
const getParenthesisEndTests: TestGetParenthesisEndObject[] = [
    {
        description: "Simple case with no nesting",
        in: "(abc)",
        start: 0,
        end: 4
    },
    {
        description: "Nested parenthesis",
        in: "(a(b)c)",
        start: 0,
        end: 6
    },
    {
        description: "Parenthesis with strings that contain parenthesis",
        in: "(a(\"(\")b)",
        start: 0,
        end: 8
    },
    {
        description: "Parenthesis inside a string should be ignored",
        in: "(\"a)b\")",
        start: 0,
        end: 6
    },
    {
        description: "Complex nested parenthesis",
        in: "(a(b(c)d)e)",
        start: 0,
        end: 10
    },
    {
        description: "Multiple nested parenthesis groups",
        in: "(a(b)c(d)e)",
        start: 0,
        end: 10
    },
    {
        description: "Parenthesis inside strings inside parenthesis",
        in: "(a(b\"c(d)e\"f)g)",
        start: 0,
        end: 14
    },
    {
        description: "Parenthesis with no closing",
        in: "(a(b)c",
        start: 0,
        end: -1
    },
    {
        description: "Empty parenthesis",
        in: "()",
        start: 0,
        end: 1
    },
    {
        description: "Single level parenthesis in the middle of a string",
        in: "text(a)text",
        start: 4,
        end: 6
    },
    {
        description: "Nested empty parenthesis",
        in: "(a()b)",
        start: 0,
        end: 5
    },
    {
        description: "Multiple parenthesis with strings and nesting",
        in: "((a)\"b(c)\"(d)e(f)g)",
        start: 0,
        end: 18
    }
]
describe("getBracketEnd", () => {
    for (const test of getParenthesisEndTests) {
        it(test.description, () => {
            const result = getParenthesisEnd(test.in, test.start);
            expect(result).toBe(test.end);
        });
    }
})

type TestSplitArgsObject = {
    description: string;
    in: string;
    separator: string;
    out: string[];
};
const getArgsTests: TestSplitArgsObject[] = [
    {
        description: 'Simple case with commas',
        in: '1,2,3',
        separator: ',',
        out: ['1', '2', '3']
    },
    {
        description: 'Simple case with spaces',
        in: '1 2 3',
        separator: ' ',
        out: ['1', '2', '3']
    },
    {
        description: 'Nested parenthesis with commas',
        in: 'func(1,2),3',
        separator: ',',
        out: ['func(1,2)', '3']
    },
    {
        description: 'Quotes inside arguments with commas',
        in: '"text,arg1","text,arg2"',
        separator: ',',
        out: ['"text,arg1"', '"text,arg2"']
    },
    {
        description: 'Parenthesis and quotes combined with commas',
        in: 'func("text,arg1", (x,y)), 3',
        separator: ',',
        out: ['func("text,arg1", (x,y))', '3']
    },
    {
        description: 'Escaped quotes within arguments with commas',
        in: '"arg\\",test1","arg2"',
        separator: ',',
        out: ['"arg\\",test1"', '"arg2"']
    },
    {
        description: 'Multiple nested structures with commas',
        in: 'func1(func2(1,2),"text,arg3"),4',
        separator: ',',
        out: ['func1(func2(1,2),"text,arg3")', '4']
    },
    {
        description: 'Lone quote in argument with commas',
        in: 'arg1,"arg2"',
        separator: ',',
        out: ['arg1', '"arg2"']
    },
    {
        description: 'Trailing comma',
        in: 'arg1,arg2,',
        separator: ',',
        out: ['arg1', 'arg2']
    },
    {
        description: 'Trailing comma with space',
        in: 'arg1,arg2, ',
        separator: ',',
        out: ['arg1', 'arg2']
    },
    {
        description: 'Empty input',
        in: '',
        separator: ',',
        out: []
    },
    {
        description: 'Single argument with parenthesis',
        in: 'func(arg)',
        separator: ',',
        out: ['func(arg)']
    },
    {
        description: 'Single argument with quotes',
        in: '"arg"',
        separator: ',',
        out: ['"arg"']
    },
];
describe('splitArgs', () => {
    for (const test of getArgsTests) {
        it(test.description, () => {
            const result = splitArgs(test.in, test.separator);
            expect(result).toEqual(test.out);
        });
    }
});

type TestWildcardMatchStrObject = {
    description: string;
    in_pattern: string;
    in_string: string;
    out: boolean;
}
const wildcardMatchStrTest: TestWildcardMatchStrObject[] = [
    {description: '* match start', in_pattern: '*df', in_string: 'asdf', out: true},
    {description: '* match center', in_pattern: 'a*f', in_string: 'asdf', out: true},
    {description: '* matches empty string', in_pattern: 'a*f', in_string: 'af', out: true},
    {description: '* negative test', in_pattern: 'a*f', in_string: 'abc', out: false},
    {description: '_ matches single char', in_pattern: 'a_c', in_string: 'abc', out: true},
    {description: '_ not matches multiple char', in_pattern: 'a_d', in_string: 'abcd', out: false},
    {description: '_ negative test', in_pattern: 'a_f', in_string: 'abc', out: false},
    {description: 'chaining multiple _', in_pattern: 'a__f', in_string: 'abcf', out: true},
    {description: 'matches floating', in_pattern: 'b_d', in_string: 'abcde', out: true},
]
describe('matchWildcardStr', () => {
    for (const test of wildcardMatchStrTest) {
        it(test.description, () => {
            const result = wildcard_match_str(test.in_pattern, test.in_string);
            expect(result).toEqual(test.out);
        });
    }
})

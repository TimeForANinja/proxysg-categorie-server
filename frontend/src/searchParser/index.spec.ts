import {
    BuildSyntaxTree,
} from './index';

type TestParserObject = {
    description: string;
    in: string;
    out: string;
};
const parserTests: TestParserObject[] = [
    {description: 'only text', in: 'asdf', out: 'root([text_or_column("asdf")])'},
    {description: 'key-val-pair', in: 'key=val', out: 'root([key-val(root([text_or_column("key")]), root([text_or_column("val")]))])'},
    {description: 'key-val-pair with spaces', in: 'key = val', out: 'root([key-val(root([text_or_column("key")]), root([text_or_column("val")]))])'},
    {description: 'mixed use of text and key = Val', in: 'asdf key = val', out: 'root([text_or_column("asdf"), key-val(root([text_or_column("key")]), root([text_or_column("val")]))])'},
    {description: 'mixed use of text and key = Val', in: 'key = val asdf', out: 'root([key-val(root([text_or_column("key")]), root([text_or_column("val")])), text_or_column("asdf")])'},
    {description: 'handles braces', in: '(asdf) key = val', out: 'root([func(, [root([text_or_column("asdf")])]), key-val(root([text_or_column("key")]), root([text_or_column("val")]))])'},
    {description: 'handles quotes', in: '"asdf yey"', out: 'root([text("asdf yey")])'},
    {description: 'handles quoted and key=val', in: '"asdf yey" key=val', out: 'root([text("asdf yey"), key-val(root([text_or_column("key")]), root([text_or_column("val")]))])'},
    {description: 'handles chained AND', in: 'a AND b AND c AND d AND e', out: 'root([logic(AND, [logic(AND, [logic(AND, [logic(AND, [text_or_column("a"), text_or_column("b")]), text_or_column("c")]), text_or_column("d")]), text_or_column("e")])])'},
    {description: 'handles AND and OR', in: 'a AND b OR c', out: 'root([logic(OR, [logic(AND, [text_or_column("a"), text_or_column("b")]), text_or_column("c")])])'},
    {description: 'handles NOT', in: 'NOT a', out: 'root([not([text_or_column("a")])])'},
    {description: 'handles NOT with complex expressions', in: 'NOT key = val', out: 'root([not([key-val(root([text_or_column("key")]), root([text_or_column("val")]))])])'},
    {description: 'handles NOT with AND', in: 'NOT a AND b', out: 'root([logic(AND, [not([text_or_column("a")]), text_or_column("b")])])'},
    {description: 'handles NOT with OR', in: 'a OR NOT b', out: 'root([logic(OR, [text_or_column("a"), not([text_or_column("b")])])])'},
];
describe('Parser', () => {
    for (const test of parserTests) {
        it(test.description, () => {
            const tree = BuildSyntaxTree(test.in, []);
            const calc = tree.print();
            expect(calc).toBe(test.out);
        });
    }
});
const parserInvalidTests: TestParserObject[] = [
    {description: 'uneven quotes', in: 'as"df', out: 'Mismatched quotes'},
    {description: 'uneven parenthesis', in: 'as(df', out: 'Mismatched parenthesis'},
    {description: 'uneven parenthesis due to quotes', in: 'as("df)"', out: 'Mismatched parenthesis'},
    {description: 'invalid arg count for func', in: 'abs(2, 3)', out: 'Invalid arguments for function "abs"'},
    {description: 'NOT at the end', in: 'a AND NOT', out: 'NOT at the end is not allowed'},
];
describe('Parser - Invalid Input', () => {
    for (const test of parserInvalidTests) {
        it(test.description, () => {
            expect(
                () => BuildSyntaxTree(test.in, []),
            ).toThrow(test.out);
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
    {description: 'OR defaults to false', in: 'a OR b', row: {_raw: 'cd'}, out: false},
    {description: 'NOT simple string match', in: 'NOT e', row: {_raw: "test"}, out: false},
    {description: 'NOT simple string non-match', in: 'NOT x', row: {_raw: "test"}, out: true},
    {description: 'NOT key-val test', in: 'NOT a = b', row: {_raw: "c", a: "b"}, out: false},
    {description: 'NOT with AND', in: 'NOT a AND b', row: {_raw: "ab", a: "a", b: "b"}, out: false},
    {description: 'NOT with OR true case', in: 'a OR NOT b', row: {_raw: "a", a: "a", b: "b"}, out: true},
    {description: 'NOT with OR false case', in: '(NOT a) OR NOT b', row: {_raw: "ab", a: "a", b: "b"}, out: false},
]
describe('Parser:calc', () => {
    for (const test of parserCalcTests) {
        it(test.description, () => {
            const tree = BuildSyntaxTree(test.in, []);
            const calc = tree.test(test.row);
            expect(calc).toBe(test.out);
        });
    }
})
describe('Parser:other', () => {
    it("errors when a required row field is missing", () => {
        expect(() => {
            const tree = BuildSyntaxTree(
                "a=b",
                [{ field: "c", description: "Test field that is not part of the row"}],
            );
            tree.test({a: "asdf", _raw: "test"});
        }).toThrow("Row does not contain expected field \"c\"")
    });
});

import {
    BuildSyntaxTree,
} from './index';

type TestParserObject = {
    description: string;
    in: string;
    out: string;
};
const parserTests: TestParserObject[] = [
    {description: 'only text', in: 'asdf', out: 'root([text("asdf")])'},
    {description: 'key-val-pair', in: 'key=val', out: 'root([key-val(root([column("key")]), =, root([text("val")]))])'},
    {description: 'key-val-pair with spaces', in: 'key = val', out: 'root([key-val(root([column("key")]), =, root([text("val")]))])'},
    {description: 'mixed use of text and key = Val', in: 'asdf key = val', out: 'root([text("asdf"), key-val(root([column("key")]), =, root([text("val")]))])'},
    {description: 'mixed use of text and key = Val', in: 'key = val asdf', out: 'root([key-val(root([column("key")]), =, root([text("val")])), text("asdf")])'},
    {description: 'handles braces', in: '(asdf) key = val', out: 'root([func(, [root([text("asdf")])]), key-val(root([column("key")]), =, root([text("val")]))])'},
    {description: 'handles quotes', in: '"asdf yey"', out: 'root([text("asdf yey")])'},
    {description: 'handles quoted and key=val', in: '"asdf yey" key=val', out: 'root([text("asdf yey"), key-val(root([column("key")]), =, root([text("val")]))])'},
    {description: 'handles chained AND', in: 'a AND b AND c AND d AND e', out: 'root([logic(AND, [logic(AND, [logic(AND, [logic(AND, [text("a"), text("b")]), text("c")]), text("d")]), text("e")])])'},
    {description: 'handles AND and OR', in: 'a AND b OR c', out: 'root([logic(OR, [logic(AND, [text("a"), text("b")]), text("c")])])'},
    {description: 'handles NOT', in: 'NOT a', out: 'root([not([text("a")])])'},
    {description: 'handles NOT with complex expressions', in: 'NOT key = val', out: 'root([not([key-val(root([column("key")]), =, root([text("val")]))])])'},
    {description: 'handles NOT with AND', in: 'NOT a AND b', out: 'root([logic(AND, [not([text("a")]), text("b")])])'},
    {description: 'handles NOT with OR', in: 'a OR NOT b', out: 'root([logic(OR, [text("a"), not([text("b")])])])'},
];
describe('Parser', () => {
    for (const test of parserTests) {
        it(test.description, () => {
            const tree = BuildSyntaxTree(test.in, [{ field: "key" }]);
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
    {description: 'key-val test 01', in: 'key = b', row: {_raw: "c", key: "b"}, out: true},
    {description: 'key-val test 02', in: 'key = bc', row: {_raw: "c", key: "b"}, out: false},
    {description: 'key-val test 03', in: 'key = bc', row: {_raw: "c", key: "bcd"}, out: false},
    {description: 'complex example 01', in: 'ab OR cd', row: {_raw: "acd"}, out: true},
    {description: 'key-val wildcard 01', in: 'key = *b', row: {_raw: "c", key: "ab"}, out: true},
    {description: 'key-val not matching raw', in: 'key=b', row: {_raw: "a=b", key: "c"}, out: false},
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
            const tree = BuildSyntaxTree(
                test.in,
                Object.keys(test.row).map(x => ({ field: x })),
            );
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

    describe("raw-text argtype differentiates between string and column", () => {
        it("identifies as string if no column what that name is found", () => {
            const tree = BuildSyntaxTree("a=b", []);
            expect(tree.print()).toBe("root([key-val(root([text(\"a\")]), =, root([text(\"b\")]))])");
        })
        it("identifies column if field name is known", () => {
            const tree = BuildSyntaxTree(
                "a=b",
                [{ field: "a", description: "Test field"}],
            );
            expect(tree.print()).toBe("root([key-val(root([column(\"a\")]), =, root([text(\"b\")]))])");
        })
    })
});

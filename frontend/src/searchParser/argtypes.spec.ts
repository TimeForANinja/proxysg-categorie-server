import {
    BuildSyntaxTree,
} from './index';
import {ARG_TYPES} from "./argTypes";
import {TreeNode} from "./treeNode";

describe('key-val-pair', () => {
    // Test that the matches function properly handles escaped strings
    describe('matches function', () => {
        it('should match operator', () => {
            // Find the key-val-pair argType
            const keyValPairType = ARG_TYPES.find(type => type.name === 'key-val-pair')!;

            // Test cases with operators inside escaped strings
            expect(keyValPairType.matches('asd="df"')).toBe(true); // Valid key-val-pair
            expect(keyValPairType.matches('asd=df')).toBe(true); // Valid key-val-pair
            expect(keyValPairType.matches('asd="d=f"')).toBe(true); // Valid key-val-pair with = inside quotes
            expect(keyValPairType.matches('asd=d"=f"')).toBe(true); // Valid key-val-pair with = inside quotes
        });

        it('should not match operators inside escaped strings', () => {
            // Find the key-val-pair argType
            const keyValPairType = ARG_TYPES.find(type => type.name === 'key-val-pair')!;

            // These should not match as key-val-pairs
            expect(keyValPairType.matches('asd"=df"')).toBe(false); // = is inside an escaped string
            expect(keyValPairType.matches('"asd=df"')).toBe(false); // = is inside an escaped string
            expect(keyValPairType.matches('a"sd=d"f')).toBe(false); // = is inside an escaped string
        });
    });

    describe('Parser with extended operators', () => {
        // Test parsing of expressions with new operators
        const parserTests = [
            {
                description: 'key-val-pair with != operator',
                in: 'key != val',
                out: 'root([key-val(root([column("key")]), !=, root([text("val")]))])'
            },
            {
                description: 'key-val-pair with >= operator',
                in: 'key >= val',
                out: 'root([key-val(root([column("key")]), >=, root([text("val")]))])'
            },
            {
                description: 'key-val-pair with <= operator',
                in: 'key <= val',
                out: 'root([key-val(root([column("key")]), <=, root([text("val")]))])'
            },
            {
                description: 'ignores escaped operators',
                in: '"key=val"!=val',
                out: 'root([key-val(root([text("key=val")]), !=, root([text("val")]))])'
            },
        ];

        for (const test of parserTests) {
            it(test.description, () => {
                const tree = BuildSyntaxTree(test.in, [{field: "key"}]);
                const calc = tree.print();
                expect(calc).toBe(test.out);
            });
        }
    })

    describe('Parser:calc with extended operators', () => {
        // Test calculation of expressions with new operators
        const calcTests = [
            // != operator tests
            {description: 'key-val test with != (not equal)', in: 'key != b', row: {_raw: "c", key: "a"}, out: true},
            {description: 'key-val test with != (equal)', in: 'key != b', row: {_raw: "c", key: "b"}, out: false},
            {description: 'key-val test with != and wildcard (not equal)', in: 'key != *b', row: {_raw: "c", key: "c"}, out: true},
            {description: 'key-val test with != and wildcard (equal)', in: 'key != *b', row: {_raw: "c", key: "ab"}, out: false},

            // >= operator tests
            {description: 'key-val test with >= (greater)', in: 'key >= b', row: {_raw: "c", key: "c"}, out: true},
            {description: 'key-val test with >= (equal)', in: 'key >= b', row: {_raw: "c", key: "b"}, out: true},
            {description: 'key-val test with >= (less)', in: 'key >= b', row: {_raw: "c", key: "a"}, out: false},

            // <= operator tests
            {description: 'key-val test with <= (less)', in: 'key <= b', row: {_raw: "c", key: "a"}, out: true},
            {description: 'key-val test with <= (equal)', in: 'key <= b', row: {_raw: "c", key: "b"}, out: true},
            {description: 'key-val test with <= (greater)', in: 'key <= b', row: {_raw: "c", key: "c"}, out: false},

            // Complex tests with multiple operators
            {description: 'complex test with != and AND', in: 'key != a AND key <= c', row: {_raw: "c", key: "b"}, out: true},
            {description: 'complex test with >= and OR', in: 'key >= c OR key <= a', row: {_raw: "c", key: "b"}, out: false},
        ];

        for (const test of calcTests) {
            it(test.description, () => {
                const node = new TreeNode(
                    test.in,
                    ARG_TYPES.find(type => type.name === 'key-val-pair')!,
                    Object.keys(test.row).map(x => ({ field: x })),
                );
                const calc = node._calc(test.row);
                expect(calc).toBe(test.out);
            });
        }
    });
});

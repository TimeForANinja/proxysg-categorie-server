import {
    getIndent,
    getParents,
    computeDiff,
    buildDiff,
    AlignedDiffLine,
} from './build_diff';

describe('build_diff utility', () => {
    describe('getIndent', () => {
        it('should return 0 for no indentation', () => {
            expect(getIndent('hello')).toBe(0);
        });

        it('should return correct number of spaces', () => {
            expect(getIndent('  hello')).toBe(2);
            expect(getIndent('    hello')).toBe(4);
        });

        it('should detect lists', () => {
            expect(getIndent('- item1')).toBe(2);
            expect(getIndent('  - item2')).toBe(4);
            expect(getIndent('    - item3')).toBe(6);
        });

        it('should return 0 for empty string', () => {
            expect(getIndent('')).toBe(0);
        });
    });

    describe('getParents', () => {
        it('should correctly identify parents in a YAML-like structure', () => {
            const lines = [
                'parent:',      // 0
                '  child1: a',  // 1
                '  child2:',    // 2
                '    grandchild: b' // 3
            ];
            const parents = getParents(lines);
            expect(parents).toEqual([-1, 0, 0, 2]);
        });

        it('should handle flat structures', () => {
            const lines = [
                'a: 1',
                'b: 2',
                'c: 3'
            ];
            const parents = getParents(lines);
            expect(parents).toEqual([-1, -1, -1]);
        });
    });

    describe('computeDiff', () => {
        it('should identify unchanged lines', () => {
            const left = ['line1', 'line2'];
            const right = ['line1', 'line2'];
            const diff = computeDiff(left, right);
            expect(diff.every(l => l.type === 'unchanged')).toBe(true);
            expect(diff.length).toBe(2);
        });

        it('should identify added lines', () => {
            const left = ['line1'];
            const right = ['line1', 'line2'];
            const diff = computeDiff(left, right);
            expect(diff[1].type).toBe('added');
            expect(diff[1].right).toBe('line2');
        });

        it('should identify removed lines', () => {
            const left = ['line1', 'line2'];
            const right = ['line1'];
            const diff = computeDiff(left, right);
            expect(diff[1].type).toBe('removed');
            expect(diff[1].left).toBe('line2');
        });

        it('should identify modified lines when key matches', () => {
            const left = ['key: old value'];
            const right = ['key: new value'];
            const diff = computeDiff(left, right);
            expect(diff.length).toBe(1);
            expect(diff[0].type).toBe('modified');
            expect(diff[0].left).toBe('key: old value');
            expect(diff[0].right).toBe('key: new value');
        });
        
        it('should NOT identify modified lines when key differs', () => {
            const left = ['key1: value'];
            const right = ['key2: value'];
            const diff = computeDiff(left, right);
            expect(diff.length).toBe(2);
            expect(diff[0].type).toBe('removed');
            expect(diff[1].type).toBe('added');
        });

        it('should NOT identify modified lines when indent differs', () => {
            const left = ['  key: value'];
            const right = ['key: value'];
            const diff = computeDiff(left, right);
            expect(diff.length).toBe(2);
            expect(diff[0].type).toBe('removed');
            expect(diff[1].type).toBe('added');
        })
    });

    describe('buildDiff', () => {
        it('should include context lines around changes', () => {
            const left = [
                'root:',
                '  - l1',
                '  - l2',
                '  - l3',
                '  key: l4',
                '  - l5',
                '  - l6',
                '  - l7'
            ].join('\n');
            const right = [
                'root:',
                '  - l1',
                '  - l2',
                '  - l3',
                '  key: changed',
                '  - l5',
                '  - l6',
                '  - l7'
            ].join('\n');

            // With context 1, it should show:
            // spacer
            // - l3
            // key: changed
            // - l5
            // spacer
            const diff = buildDiff(left, right, 1);

            const types = diff.map(d => d.type);
            expect(types).toContain('spacer');
            expect(types).toContain('modified');
            expect(types).toContain('unchanged');

            // Check that 'key: changed' is there
            const modifiedLine = diff.find(d => d.type === 'modified');
            expect(modifiedLine?.right).toBe('  key: changed');
        });

        it('should preserve parent hierarchy even if far from change', () => {
            const left = 'root:\n  l1\n  l2\n  l3\n  l4\n  l5\n  leaf: old';
            const right = 'root:\n  l1\n  l2\n  l3\n  l4\n  l5\n  leaf: new';

            // With context 1, root: is far enough (6 lines away) that it shouldn't be included by context
            // It should however still show up in the diff
            const diff = buildDiff(left, right, 1);

            const hasRoot = diff.some(d => d.left === 'root:');
            expect(hasRoot).toBe(true);
        });

        it('should handle YAML list markers as indentation', () => {
            const left = 'categories:\n- cat 01\n- cat 02\n- cat 03\n- cat 04\n- cat 05';
            const right = 'categories:\n- cat 01\n- cat 02\n- cat 03\n- cat 04\n- cat 05 changed';

            // categories should not be in the contextLines for cat05
            const diff = buildDiff(left, right, 1);

            // diff should still include "categories" as parent key (next lower indentation)
            const hasHeader = diff.some(d => d.left === 'categories:');
            expect(hasHeader).toBe(true);
        });

        it('should collapse long unchanged sections into a single spacer', () => {
            const left = 'a\n'.repeat(20) + 'change\n' + 'b\n'.repeat(20);
            const right = 'a\n'.repeat(20) + 'fixed\n' + 'b\n'.repeat(20);

            const diff = buildDiff(left, right, 2);
            const spacers = diff.filter(d => d.type === 'spacer');
            expect(spacers.length).toBe(2); // One before, one after
        });

        it('should include sibling lines with same indent as parent', () => {
            const left = [
                'root:',
                '  key1: val1',
                '  key2: val2',
                '  list:',
                '    - item1',
                '    - item2'
            ].join('\n');
            const right = [
                'root:',
                '  key1: val1',
                '  key2: val2',
                '  list:',
                '    - item1',
                '    - item2 changed'
            ].join('\n');

            // context 0 to ensure we only see what is forced by hierarchy/keys
            const diff = buildDiff(left, right, 0);

            const lines = diff.filter(d => d.type !== 'spacer').map(d => (d.right || d.left)?.trim());

            expect(lines).toContain('root:');
            expect(lines).toContain('list:');
            expect(lines).toContain('- item2 changed');
            
            // key1 and key2 are shown because they are the same indent as list
            expect(lines).toContain('key1: val1');
            expect(lines).toContain('key2: val2');

            // Also - item1 is NOT shown because its indent (6) is different from its parent 'list:' (2).
            expect(lines).not.toContain('- item1');
        });

        it('should work for a full production example', () => {
            const context_lines = 3;
            const left = [
                'categories:',
                '- id: 0786c3c0-dfbc-4594-83b1-5368a2cf0477',
                '  name: test-cat-01',
                '  description: Hello World',
                '  color: 47321',
                '  children:',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0471 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0472 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0473 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0474 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0475 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0476 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0478 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0479 (test-cat-01)',
                '- id: 74360645-8fdd-4d58-9724-3f6245d10e82',
                '  name: test-cat-02',
                '  description: \'\'',
                '  color: 34650',
                '  children: []',
                '- id: LIST_RFC_SPECIAL_USE',
                '  name: RFC-Listed-Special-Use-URLs',
                '  description: RFC6761 Special-Use Domain Names',
                '  color: 0',
                '  children:',
                '  - LIST_TLD (Public-TLDs)',
                '  - LIST_RFC_SPECIAL_USE (RFC-Listed-Special-Use-URLs)',
                '  - LIST_RFC_SPECIAL_USE (RFC-Listed-Special-Use-URLs)',
                '  - LIST_RFC_SPECIAL_USE (RFC-Listed-Special-Use-URLs)',
                '- id: LIST_TLD',
                '  name: Public-TLDs',
                '  description: header',
                '  color: 0',
                '  children: []',
                '',
                'tokens:',
                '- id: d2e87bd2-e80a-4468-9e10-d4ab5a237ad9',
                '  token_value: a121e6cf-62c7-4023-bae2-a4ba1c45eeaf',
                '  description: tok01',
                '  categories:',
                '  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '  - LIST_TLD (Public-TLDs)',
                '',
                'urls:',
                '- id: 033fc9cc-5d60-47dd-a631-81e89ad03b29',
                '  url: s3.amazonaws.com',
                '  description: \'\'',
                '  categories: []',
                '- id: 3d00440d-0283-40a9-9a94-dc9f19db91b8',
                '  url: facebook.com',
                '  description: \'\'',
                '  categories:',
                '  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)',
                '- id: 48a8c763-7e65-4e4a-b54b-88f499e43d3c',
                '  url: heise.de',
                '  description: \'\'',
                '  categories:',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '- id: 4eeb6750-6882-4396-816a-2f5f9424e46e',
                '  url: localhost',
                '  description: \'\'',
                '  categories:',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '- id: 6c935b8c-47c7-4634-836f-74015899f2e1',
                '  url: home.corp',
                '  description: \'\'',
                '  categories:',
                '  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)',
                '  - LIST_TLD (Public-TLDs)',
            ].join('\n');
            const right = [
                'categories:',
                '- id: 0786c3c0-dfbc-4594-83b1-5368a2cf0477',
                '  name: test-cat-01',
                '  description: Hello World',
                '  color: 47321',
                '  children:',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0471 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0472 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0473 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0474 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0476 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0478 (test-cat-01)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0479 (test-cat-01)',
                '- id: 74360645-8fdd-4d58-9724-3f6245d10e82',
                '  name: test-cat-02',
                '  description: \'\'',
                '  color: 34650',
                '  children: []',
                '- id: LIST_RFC_SPECIAL_USE',
                '  name: RFC-Listed-Special-Use-URLs',
                '  description: RFC6761 Special-Use Domain Names',
                '  color: 0',
                '  children:',
                '  - LIST_TLD (Public-TLDs)',
                '  - LIST_RFC_SPECIAL_USE (RFC-Listed-Special-Use-URLs)',
                '  - LIST_RFC_SPECIAL_USE (RFC-Listed-Special-Use-URLs)',
                '  - LIST_RFC_SPECIAL_USE (RFC-Listed-Special-Use-URLs)',
                '- id: LIST_TLD',
                '  name: Public-TLDs',
                '  description: header',
                '  color: 0',
                '  children:',
                '  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '  - LIST_TLD (Public-TLDs)',
                '',
                'tokens:',
                '- id: d2e87bd2-e80a-4468-9e10-d4ab5a237ad9',
                '  token_value: a121e6cf-62c7-4023-bae2-a4ba1c45eeaf',
                '  description: tok01',
                '  categories:',
                '  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '  - LIST_TLD (Public-TLDs)',
                '',
                'urls:',
                '- id: 033fc9cc-5d60-47dd-a631-81e89ad03b29',
                '  url: s3.amazonaws.com',
                '  description: \'\'',
                '  categories: []',
                '- id: 3d00440d-0283-40a9-9a94-dc9f19db91b8',
                '  url: facebook.com',
                '  description: \'\'',
                '  categories:',
                '  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)',
                '- id: 48a8c763-7e65-4e4a-b54b-88f499e43d3c',
                '  url: heise.de',
                '  description: well known tech portal',
                '  categories:',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '- id: 4eeb6750-6882-4396-816a-2f5f9424e46e',
                '  url: localhost',
                '  description: \'\'',
                '  categories:',
                '  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)',
                '- id: 6c935b8c-47c7-4634-836f-74015899f2e1',
                '  url: home.corp',
                '  description: \'\'',
                '  categories:',
                '  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)',
                '  - LIST_TLD (Public-TLDs)',
            ].join('\n');

            const expected: AlignedDiffLine[] = [
                {
                    "type": "unchanged",
                    "left": "categories:",
                    "right": "categories:"
                },
                {
                    "type": "unchanged",
                    "left": "- id: 0786c3c0-dfbc-4594-83b1-5368a2cf0477",
                    "right": "- id: 0786c3c0-dfbc-4594-83b1-5368a2cf0477"
                },
                {
                    "type": "unchanged",
                    "left": "  name: test-cat-01",
                    "right": "  name: test-cat-01"
                },
                {
                    "type": "unchanged",
                    "left": "  description: Hello World",
                    "right": "  description: Hello World"
                },
                {
                    "type": "unchanged",
                    "left": "  color: 47321",
                    "right": "  color: 47321"
                },
                {
                    "type": "unchanged",
                    "left": "  children:",
                    "right": "  children:"
                },
                {
                    "type": "spacer"
                },
                {
                    "type": "unchanged",
                    "left": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0472 (test-cat-01)",
                    "right": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0472 (test-cat-01)"
                },
                {
                    "type": "unchanged",
                    "left": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0473 (test-cat-01)",
                    "right": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0473 (test-cat-01)"
                },
                {
                    "type": "unchanged",
                    "left": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0474 (test-cat-01)",
                    "right": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0474 (test-cat-01)"
                },
                {
                    "type": "removed",
                    "left": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0475 (test-cat-01)"
                },
                {
                    "type": "unchanged",
                    "left": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0476 (test-cat-01)",
                    "right": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0476 (test-cat-01)"
                },
                {
                    "type": "unchanged",
                    "left": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)",
                    "right": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)"
                },
                {
                    "type": "unchanged",
                    "left": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0478 (test-cat-01)",
                    "right": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0478 (test-cat-01)"
                },
                {
                    "type": "spacer"
                },
                {
                    "type": "unchanged",
                    "left": "- id: LIST_TLD",
                    "right": "- id: LIST_TLD"
                },
                {
                    "type": "unchanged",
                    "left": "  name: Public-TLDs",
                    "right": "  name: Public-TLDs"
                },
                {
                    "type": "unchanged",
                    "left": "  description: header",
                    "right": "  description: header"
                },
                {
                    "type": "unchanged",
                    "left": "  color: 0",
                    "right": "  color: 0"
                },
                {
                    "type": "modified",
                    "left": "  children: []",
                    "right": "  children:"
                },
                {
                    "type": "added",
                    "right": "  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)"
                },
                {
                    "type": "added",
                    "right": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)"
                },
                {
                    "type": "added",
                    "right": "  - LIST_TLD (Public-TLDs)"
                },
                {
                    "type": "unchanged",
                    "left": "",
                    "right": ""
                },
                {
                    "type": "unchanged",
                    "left": "tokens:",
                    "right": "tokens:"
                },
                {
                    "type": "unchanged",
                    "left": "- id: d2e87bd2-e80a-4468-9e10-d4ab5a237ad9",
                    "right": "- id: d2e87bd2-e80a-4468-9e10-d4ab5a237ad9"
                },
                {
                    "type": "spacer"
                },
                {
                    "type": "unchanged",
                    "left": "urls:",
                    "right": "urls:"
                },
                {
                    "type": "spacer"
                },
                {
                    "type": "unchanged",
                    "left": "  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)",
                    "right": "  - 74360645-8fdd-4d58-9724-3f6245d10e82 (test-cat-02)"
                },
                {
                    "type": "unchanged",
                    "left": "- id: 48a8c763-7e65-4e4a-b54b-88f499e43d3c",
                    "right": "- id: 48a8c763-7e65-4e4a-b54b-88f499e43d3c"
                },
                {
                    "type": "unchanged",
                    "left": "  url: heise.de",
                    "right": "  url: heise.de"
                },
                {
                    "type": "modified",
                    "left": "  description: ''",
                    "right": "  description: well known tech portal"
                },
                {
                    "type": "unchanged",
                    "left": "  categories:",
                    "right": "  categories:"
                },
                {
                    "type": "unchanged",
                    "left": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)",
                    "right": "  - 0786c3c0-dfbc-4594-83b1-5368a2cf0477 (test-cat-01)"
                },
                {
                    "type": "unchanged",
                    "left": "- id: 4eeb6750-6882-4396-816a-2f5f9424e46e",
                    "right": "- id: 4eeb6750-6882-4396-816a-2f5f9424e46e"
                },
                {
                    "type": "spacer"
                }
            ];

            const diff = buildDiff(left, right, context_lines);

            expect(diff.length).toBe(expected.length);

            for (let i = 0; i < diff.length; i++) {
                const is = diff[i];
                const should = expected[i];
                expect(is.type).toBe(should.type);
                expect(is.left).toBe(should.left);
                expect(is.right).toBe(should.right);
            }
        });
    });
});

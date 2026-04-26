export interface AlignedDiffLine {
    left?: string;
    right?: string;
    type: 'unchanged' | 'added' | 'removed' | 'modified' | 'spacer';
    leftIndex?: number;
    rightIndex?: number;
    indentLevel?: number;
    isList?: boolean;
}

export const DEFAULT_CONTEXT_LINES = 3;

/**
 * Calculates the indentation level of a line (number of leading spaces).
 */
export function getIndent(line: string): number {
    const match = line.match(/^(\s*)/);
    let indent = match ? match[1].length : 0;

    // YAML list items are logically deeper than their parent key,
    // even if they share the same base indentation level.
    if (line.trim().startsWith('- ')) {
        indent += 2;
    }

    return indent;
}

/**
 * Finds the parent line index for each line in a list of lines based on YAML-style indentation.
 * A parent is the nearest preceding line with less indentation.
 * Returns an array where the value at index i is the index of the parent of line i.
 */
export function getParents(lines: string[]): number[] {
    const parents = new Array(lines.length).fill(-1);
    const stack: { indent: number, index: number }[] = [];
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (!line || line.trim().length === 0) continue;
        const indent = getIndent(line);

        while (stack.length > 0) {
            const top = stack[stack.length - 1];
            if (top.indent < indent) break;
            
            // Special case for YAML: a list item (- key: val) is the parent of 
            // subsequent keys at the same indentation level (  key2: val2).
            const topIsList = isListItem(lines[top.index]);
            const currentIsList = isListItem(line);
            if (top.indent === indent && topIsList && !currentIsList) {
                break;
            }
            
            stack.pop();
        }

        if (stack.length > 0) {
            parents[i] = stack[stack.length - 1].index;
        }
        stack.push({ indent, index: i });
    }
    return parents;
}

/**
 * Computes the Longest Common Subsequence (LCS) matrix for two arrays of strings.
 * This is used as the base for the diffing algorithm to find aligned lines.
 * Uses Int32Array for memory efficiency in larger diffs.
 */
function lcs(left: string[], right: string[]) {
    const m = left.length;
    const n = right.length;
    const dp = Array.from({ length: m + 1 }, () => new Int32Array(n + 1));

    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            if (left[i - 1] === right[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + 1;
            } else {
                dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
            }
        }
    }
    return dp;
}

/**
 * Aligns two sets of lines and identifies additions, removals, and modifications.
 * It uses the LCS matrix to backtrack and find the optimal alignment.
 * After initial alignment, it merges adjacent 'removed' and 'added' lines 
 * with the same key/indent into a 'modified' type.
 */
export function computeDiff(left: string[], right: string[]): AlignedDiffLine[] {
    const dp = lcs(left, right);
    const result: AlignedDiffLine[] = [];
    let i = left.length;
    let j = right.length;

    while (i > 0 || j > 0) {
        let line: AlignedDiffLine;
        if (i > 0 && j > 0 && left[i - 1] === right[j - 1]) {
            line = {
                left: left[i - 1],
                right: right[j - 1],
                type: 'unchanged',
                leftIndex: i - 1,
                rightIndex: j - 1
            };
            i--;
            j--;
        } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
            line = {
                right: right[j - 1],
                type: 'added',
                rightIndex: j - 1
            };
            j--;
        } else {
            line = {
                left: left[i - 1],
                type: 'removed',
                leftIndex: i - 1
            };
            i--;
        }
        const content = line.left || line.right || "";
        line.indentLevel = getIndent(content);
        line.isList = isListItem(content);
        result.unshift(line);
    }

    // Post-process to detect "modified" lines.
    // We group consecutive changes (removals and additions) and try to match them
    // by key and indentation. This improves the diff for YAML structures.
    let k = 0;
    while (k < result.length) {
        if (result[k].type === 'unchanged') {
            k++;
            continue;
        }

        // Identify the bounds of the current change block
        let blockEnd = k;
        while (blockEnd < result.length && result[blockEnd].type !== 'unchanged') {
            blockEnd++;
        }

        // Collect indices of removals and additions in this block
        const removals = [];
        const additions = [];
        for (let m = k; m < blockEnd; m++) {
            if (result[m].type === 'removed') removals.push(m);
            else if (result[m].type === 'added') additions.push(m);
        }

        // Try to match each removal with an addition based on key and indent
        for (const rIdx of removals) {
            const leftLine = result[rIdx].left || "";
            const leftKey = leftLine.split(':')[0].trim();
            // Do not match list items or empty keys (like just whitespace or comments)
            if (leftKey === "" || leftLine.trim().startsWith('- ')) continue;
            const leftIndent = getIndent(leftLine);

            for (let i = 0; i < additions.length; i++) {
                const aIdx = additions[i];
                if (aIdx === -1) continue;
                
                const rightLine = result[aIdx].right || "";
                const rightKey = rightLine.split(':')[0].trim();
                const rightIndent = getIndent(rightLine);

                if (leftKey === rightKey && leftIndent === rightIndent) {
                    // We found a match, so we convert the 'removed' line into 'modified'
                    // and mark the 'added' line for deletion from the results.
                    result[rIdx] = {
                        left: leftLine,
                        right: rightLine,
                        type: 'modified',
                        leftIndex: result[rIdx].leftIndex,
                        rightIndex: result[aIdx].rightIndex,
                        indentLevel: result[rIdx].indentLevel,
                        isList: result[rIdx].isList
                    };
                    result[aIdx].type = 'spacer'; // Temporary marker for removal
                    additions[i] = -1;
                    break;
                }
            }
        }

        // Clean up matched additions from the block
        for (let m = blockEnd - 1; m >= k; m--) {
            if (result[m].type === 'spacer') {
                result.splice(m, 1);
                blockEnd--;
            }
        }
        k = blockEnd;
    }

    return result;
}

/**
 * Helper to check if a line is a YAML list item.
 */
function isListItem(line: string | undefined): boolean {
    if (!line) return false;
    return line.trim().startsWith('- ');
}

/**
 * Minifies the aligned diff by hiding unchanged sections,
 * while preserving structural relationships like list items.
 *
 * a) For unchanged lines, show context lines around them.
 * b) Show list items and their siblings, preserving indentation.
 * c) Show parent list items for modified lines.
 */
export function minify(aligned: AlignedDiffLine[], contextLines: number = DEFAULT_CONTEXT_LINES): AlignedDiffLine[] {
    const showFlags = new Array(aligned.length).fill(false);

    // mark changed lines + context around it
    for (let i = 0; i < aligned.length; i++) {
        if (aligned[i].type !== 'unchanged') {
            for (let k = Math.max(0, i - contextLines); k <= Math.min(aligned.length - 1, i + contextLines); k++) {
                showFlags[k] = true;
            }
        }
    }

    // force parent keys to show, but only for modified lines and not the ctx lines around it
    const simple_content = aligned.map(line => line.left || line.right || "");
    const parent_map = getParents(simple_content);
    for (let i = 0; i < aligned.length; i++) {
        if (aligned[i].type !== 'unchanged') {
            let parent = parent_map[i];
            while (parent !== -1) {
                showFlags[parent] = true;
                // also include rows below the parent as long as their indent is identical
                let next_to_parent = parent + 1;
                while (getIndent(simple_content[next_to_parent]) == getIndent(simple_content[parent])) {
                    showFlags[next_to_parent] = true;
                    next_to_parent++;
                }
                parent = parent_map[parent];
            }
        }
    }

    // Assemble final result with spacers
    const result: AlignedDiffLine[] = [];
    let inSpacer = false;
    for (let i = 0; i < aligned.length; i++) {
        if (showFlags[i]) {
            result.push(aligned[i]);
            inSpacer = false;
        } else if (!inSpacer) {
            result.push({ type: 'spacer', indentLevel: 0, isList: false });
            inSpacer = true;
        }
    }
    return result;
}

/**
 * Main function to build a formatted diff between two strings.
 * 1. Splits input into lines.
 * 2. Computes the aligned diff with metadata.
 * 3. Minifies the result based on structural rules.
 */
export function buildDiff(leftContent: string, rightContent: string, contextLines: number = DEFAULT_CONTEXT_LINES): AlignedDiffLine[] {
    const leftLines = leftContent.split('\n');
    const rightLines = rightContent.split('\n');
    
    const aligned = computeDiff(leftLines, rightLines);
    return minify(aligned, contextLines);
}

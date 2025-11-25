import React from 'react';

export interface UseSlidingWindowOptions {
  /** Maximum number of items visible at once */
  windowSize?: number;
  /** How many items to shift the window per action */
  step?: number;
  /**
   * When any of these values change, the window resets to the initial state
   * (top/oldest-first by default).
   */
  resetKeys?: React.DependencyList;
}

export interface UseSlidingWindowResult {
  startIndex: number;
  endIndex: number; // exclusive — matches Array.prototype.slice end param semantics
  /** Count of items hidden above the current window */
  topHidden: number;
  /** Count of items hidden below the current window */
  bottomHidden: number;
  /** Slide the window up (towards the top/beginning) by `step` */
  showMoreTop: () => void;
  /** Slide the window down (towards the bottom/end) by `step` */
  showMoreBottom: () => void;
  /** Replace the current window explicitly by setting the starting index. */
  setWindow: (start: number) => void;
}

/**
 * Reusable sliding-window pagination state.
 *
 * Notes on indices and "exclusive" end:
 * - The window is represented by `[startIndex, endIndex)` where `endIndex` is exclusive.
 *   This matches `Array.prototype.slice(start, end)` semantics and is convenient for rendering
 *   with `items.slice(startIndex, endIndex)`.
 * - Example: if `startIndex = 5` and `endIndex = 10`, the visible items are indices 5..9 (5 items).
 *
 * Behavior:
 * - Keeps a fixed-size window (default 500) over a list of length `total`.
 * - Moves in steps (default 100) while clamping to boundaries.
 * - Resets to the first/top window when `total` or any `resetKeys` change.
 */
export function useSlidingWindow(
  total: number,
  options: UseSlidingWindowOptions = {}
): UseSlidingWindowResult {
  const windowSize = options.windowSize ?? 500;
  const step = options.step ?? 100;

  const initialEnd = Math.min(windowSize, total);
  const [startIndex, setStartIndex] = React.useState(0);
  const [endIndex, setEndIndex] = React.useState(initialEnd);

  // Reset when total or any reset key changes
  React.useEffect(() => {
    const end = Math.min(windowSize, total);
    setStartIndex(0);
    setEndIndex(end);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [total, windowSize, ...(options.resetKeys ?? [])]);

  const setWindow = React.useCallback((start: number) => {
    const size = Math.min(windowSize, total);
    // Clamp start so that the window of `size` fits into [0, total]
    const clampedStart = Math.max(0, Math.min(start, Math.max(0, total - size)));
    const clampedEnd = Math.min(total, clampedStart + size);
    setStartIndex(clampedStart);
    setEndIndex(clampedEnd);
  }, [total, windowSize]);

  const showMoreTop = React.useCallback(() => {
    if (startIndex === 0) return; // already at top
    const size = Math.min(windowSize, total);
    const newStart = Math.max(0, startIndex - step);
    const newEnd = Math.min(total, newStart + size);
    setStartIndex(newStart);
    setEndIndex(newEnd);
  }, [startIndex, total, windowSize, step]);

  const showMoreBottom = React.useCallback(() => {
    if (endIndex >= total) return; // already at bottom
    const size = Math.min(windowSize, total);
    const newEnd = Math.min(total, endIndex + step);
    const newStart = Math.max(0, newEnd - size);
    setStartIndex(newStart);
    setEndIndex(newEnd);
  }, [endIndex, total, windowSize, step]);

  const topHidden = startIndex;
  const bottomHidden = Math.max(0, total - endIndex);

  return {
    startIndex,
    endIndex,
    topHidden,
    bottomHidden,
    showMoreTop,
    showMoreBottom,
    setWindow,
  };
}

export default useSlidingWindow;

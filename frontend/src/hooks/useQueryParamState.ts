import React from "react";
import { useSearchParams } from "react-router-dom";
import { useDebounce } from "./useDebounce";

export interface UseQueryParamStateOptions {
    /** Query parameter name to synchronize with (default: 'q') */
    param?: string;
    /** Debounce time in milliseconds for writing to the URL (default: 300) */
    debounceMs?: number;
    /** Use history.replace instead of push to avoid polluting history (default: true) */
    replace?: boolean;
    /** Fallback when the param is missing (default: empty string) */
    initial?: string;
}

export interface UseQueryParamStateResult {
    /** Current input value mirrored with the URL query param */
    value: string;
    /** Setter for the input value */
    setValue: React.Dispatch<React.SetStateAction<string>>;
    /** Debounced value, useful for expensive operations depending on input */
    debounced: string;
}

/**
 * A small reusable hook that keeps a string state in sync with a URL query parameter.
 * - Initializes from the URL and reacts to external changes.
 * - Writes back to the URL when the debounced value changes.
 * - Deletes the param when the value is empty.
 * - Uses `replace` updates by default to avoid polluting history on each keystroke.
 */
export function useQueryParamState(options?: UseQueryParamStateOptions): UseQueryParamStateResult {
    const {
        param = "q",
        debounceMs = 300,
        replace = true,
        initial = "",
    } = options || {};

    const [searchParams, setSearchParams] = useSearchParams();
    // Initialize from the current URL to avoid clearing the param on first load/refresh
    const [value, setValue] = React.useState<string>(() => searchParams.get(param) ?? initial);

    // Debounced value for consumers and URL updates
    const debounced = useDebounce(value, debounceMs);

    // URL -> local state (initial + external changes)
    React.useEffect(() => {
        const raw = searchParams.get(param) ?? initial;
        if (raw !== value) {
            setValue(raw);
        }
        // We intentionally depend on searchParams and param to react on URL changes
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [searchParams, param]);

    // Local debounced -> URL
    React.useEffect(() => {
        const current = searchParams.get(param) ?? initial;
        const nextVal = debounced ?? "";
        if (current === nextVal) return;

        const next = new URLSearchParams(searchParams);
        if (nextVal && nextVal.length > 0) {
            next.set(param, nextVal);
        } else {
            next.delete(param);
        }
        setSearchParams(next, { replace });
        // We intentionally include dependencies that affect URL syncing only
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [debounced, param, replace]);

    return { value, setValue, debounced };
}

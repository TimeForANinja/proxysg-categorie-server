import React from "react";
import TablePagination from "@mui/material/TablePagination";

interface MyPaginatorProps<T> {
    filteredRows: T[],
    comparator: (a: T, b: T) => number,
    onVisibleRowsChange: (visibleRows: T[]) => void,
}
export function MyPaginator<T>({
    filteredRows,
    comparator,
    onVisibleRowsChange,
}: MyPaginatorProps<T>) {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(50);

    // reset page when filtered rows change
    React.useEffect(() => {
        setPage(0);
    }, [filteredRows.length]);

    // clip the page to the last page (in case the number of filtered rows changed)
    const maxPage = Math.max(0, Math.ceil(filteredRows.length / rowsPerPage) - 1);
    const clippedPage = Math.min(maxPage, page);

    // user navigates to the next/prev page
    const handleChangePage = (_event: unknown, newPage: number) => {
        setPage(newPage);
    };

    // user selects a different number of rows per page
    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        const oldPerPage = rowsPerPage;
        const newPerPage = parseInt(event.target.value, 10);
        // recalculate position - the previous top row will be kept on the page
        setPage(Math.floor((clippedPage * oldPerPage) / newPerPage));
        setRowsPerPage(newPerPage);
    };

    const visibleRows = React.useMemo(() => {
        // create a copy, sort and slice the rows
        return [...filteredRows]
            .sort(comparator)
            .slice(clippedPage * rowsPerPage, clippedPage * rowsPerPage + rowsPerPage);
    }, [filteredRows, comparator, clippedPage, rowsPerPage]);

    // notify parent component of visible rows change
    React.useEffect(() => {
        onVisibleRowsChange(visibleRows);
    }, [onVisibleRowsChange, visibleRows]);

    return (
        <TablePagination
            rowsPerPageOptions={[20, 50, 100]}
            component="div"
            count={filteredRows.length}
            rowsPerPage={rowsPerPage}
            page={clippedPage}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
        />
    );
}

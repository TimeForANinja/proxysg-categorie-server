import React from "react";
import TablePagination from "@mui/material/TablePagination";

interface MyPaginatorProps<T> {
    filteredRows: T[],
    comparator: (a: T, b: T) => number,
    onVisibleRowsChange: (visibleRows: T[]) => void,
}
export function MyPaginator<T>(props: MyPaginatorProps<T>) {
    const {filteredRows, comparator, onVisibleRowsChange} = props;

    // paginator settings
    const [_page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(50);

    // clip the page to the last page
    // in case the number of filtered rows changed to being smaller than for a previous search
    const _maxPage = Math.floor(filteredRows.length / rowsPerPage) - 1;
    const clippedPage = Math.max(0, Math.min(_maxPage, _page));

    // user navigates to the next/prev page
    const handleChangePage = (_event: unknown, newPage: number) => {
        setPage(newPage);
    }

    // a user selects a different number of rows per page
    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        const oldPerPage = rowsPerPage;
        const newPerPage = parseInt(event.target.value, 10);
        // recalculate position
        // the previous top row will be kept on the page
        setPage(Math.floor((clippedPage * oldPerPage) / newPerPage));
        // adjust rows per page as requested
        setRowsPerPage(newPerPage);
    };

    // calculate the rows selected by paginator
    const visibleRows = React.useMemo(
        () => filteredRows.sort(comparator).slice(
            clippedPage * rowsPerPage,
            clippedPage * rowsPerPage + rowsPerPage,
        ),
        [comparator, filteredRows, clippedPage, rowsPerPage],
    );

    // notify the parent about changes to the visible rows
    React.useEffect(
        () => onVisibleRowsChange(visibleRows),
        [onVisibleRowsChange, visibleRows],
    )

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
    )
}
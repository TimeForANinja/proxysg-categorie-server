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
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(50);

    // user navigates to the next/prev page
    const handleChangePage = (_event: unknown, newPage: number) => {
        setPage(newPage);
    }

    // a user selects a different number of rows per page
    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        // TODO: recalculate position
        setPage(0);
    };

    // calculate the rows selected by paginator
    const visibleRows = React.useMemo(
        () =>
            filteredRows.sort(comparator).slice(
                page * rowsPerPage,
                page * rowsPerPage + rowsPerPage,
            ),
        [comparator, filteredRows, page, rowsPerPage],
    );

    // notify the parent about changes to the visible rows
    React.useEffect(() => {
        onVisibleRowsChange(visibleRows);
    }, [onVisibleRowsChange, visibleRows])

    return (
        <TablePagination
            rowsPerPageOptions={[20, 50, 100]}
            component="div"
            count={filteredRows.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
        />
    )
}
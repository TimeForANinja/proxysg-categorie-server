import TablePagination from "@mui/material/TablePagination";
import React from "react";

export function MyPaginator<T>(props: {
    filteredRows: T[],
    comparator: (a: T, b: T) => number,
    onVisibleRowsChange: (visibleRows: T[]) => void,
}) {
    const {filteredRows, comparator, onVisibleRowsChange} = props;

    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(50);

    const handleChangePage = (_event: unknown, newPage: number) => {
        setPage(newPage);
    }

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const visibleRows = React.useMemo(
        () =>
            filteredRows.sort(comparator).slice(
                page * rowsPerPage,
                page * rowsPerPage + rowsPerPage,
            ),
        [comparator, filteredRows, page, rowsPerPage],
    );

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
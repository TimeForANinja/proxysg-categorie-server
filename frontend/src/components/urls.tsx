import React from 'react';
import {
    Paper, Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from "@mui/material";
import Grid from '@mui/material/Grid2';

import {getURLs} from "../api/url"
import {ListHeader} from "./shared/ListHeader";
import {MyPaginator} from "./shared/MyPaginator";
import {SearchParser} from "../searchParser";
import {getHistory} from "../api/history";
import {KVaddRAW} from "../types/stringKV";
import { useBranch } from "../hooks/useBranch";
import {URLMapping, UrlMappingFieldsRaw, URLMappingToKV} from "../types/url";

interface BuildRowProps {
    url: string,
    categories: string[],
}
/**
 * Renders a table row for a URL entry.
 *
 * Wrapped in React.memo to prevent unnecessary re-renders in the URL table.
 * This works as long as none of the props passed to the Component change
 *
 * The caching also requires us to ensure that all callbacks passed are constants (e.g., wrapped in useCallable)
 */
const BuildRow = React.memo(function BuildRow(props: BuildRowProps) {
    const { url, categories } = props;

    return (
        <React.Fragment>
            <TableRow>
                <TableCell>{url}</TableCell>
                <TableCell>
                    <Stack>
                        {
                            categories.map(c => (
                                <div key={c}>{c}</div>
                            ))
                        }
                    </Stack>
                </TableCell>
            </TableRow>
        </React.Fragment>
    )
});

function MatchingListPage() {
    const {currentBranch} = useBranch();
    // State info for the Page
    const [urls, setURLs] = React.useState<URLMapping[]>([]);

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<URLMapping[]>([]);
    const comparator = (a: URLMapping, b: URLMapping): number => a.url > b.url ? 1 : -1;
    const [quickSearch, setQuickSearch] = React.useState<SearchParser | null>(null);
    // Memoize the filtered rows to avoid unnecessary recalculations
    const filteredRows = React.useMemo(
        () => urls.filter(x => {
            return quickSearch?.test(KVaddRAW(URLMappingToKV(x))) ?? true;
        }),
        [quickSearch, urls],
    );

    // Memoize the download rows to avoid unnecessary transformations
    const downloadRows = React.useMemo(
        () => filteredRows.map(row => URLMappingToKV(row)),
        [filteredRows],
    );

    // Load urls (& Categories) From backend
    React.useEffect(() => {
        Promise.all([getURLs(currentBranch)])
            .then(([urlsData]) => {
                setURLs(urlsData);
                // fetch history async after urls and categories, since it's only needed when opening a row
                return getHistory(currentBranch);
            })
            .catch((error) => console.error("Error:", error));
    }, [currentBranch]);

    return (
        <>
            <Grid
                container
                spacing={1}
                justifyContent="center"
                alignItems="center"
            >
                <ListHeader
                    onCreate={null}
                    setQuickSearch={setQuickSearch}
                    addElement={"URL"}
                    downloadRows={downloadRows}
                    availableFields={UrlMappingFieldsRaw}
                />
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper} style={{maxHeight: 'calc(100vh - 190px)', overflow: 'auto'}}>
                            <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell />
                                        <TableCell>ID</TableCell>
                                        <TableCell>Hostname</TableCell>
                                        <TableCell>Categories</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell>BC Categories</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(urlMap =>
                                        <BuildRow
                                            url={urlMap.url}
                                            categories={urlMap.categories}
                                        />
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                        <MyPaginator
                            comparator={comparator}
                            filteredRows={filteredRows}
                            onVisibleRowsChange={setVisibleRows}
                        />
                    </Paper>
                </Grid>
            </Grid>
        </>
    );
}

export default MatchingListPage;

import React from 'react';
import {
    Box,
    Chip,
    Collapse,
    IconButton,
    Paper,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
} from "@mui/material";
import Grid from '@mui/material/Grid2';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

import {getURLs} from "../api/url"
import {ListHeader} from "./shared/ListHeader";
import {MyPaginator} from "./shared/MyPaginator";
import {SearchParser} from "../searchParser";
import {getHistory} from "../api/history";
import {KVaddRAW} from "../types/stringKV";
import { useBranch } from "../hooks/useBranch";
import {IRestURLDetail, UrlMappingFieldsRaw, URLMappingToKV} from "../types/url";
import HistoryTable from "./shared/HistoryTable";
import {IRestCommit} from "../types/history";

interface BuildRowProps {
    urlDetail: IRestURLDetail,
    branch: string,
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
    const { urlDetail, branch } = props;
    const [open, setOpen] = React.useState(false);
    const [history, setHistory] = React.useState<IRestCommit[]>([]);
    const [categorySearch, setCategorySearch] = React.useState('');

    const toggleOpen = () => {
        if (!open && history.length === 0) {
            getHistory(branch).then(setHistory).catch(console.error);
        }
        setOpen(!open);
    };

    const filteredMappings = urlDetail.categories.filter(m =>
        m.category.name.toLowerCase().includes(categorySearch.toLowerCase())
    );

    const renderCategories = () => {
        const cats = urlDetail.categories;
        const limit = 4;
        const displayed = cats.slice(0, limit);
        const remaining = cats.length - limit;

        return (
            <Stack direction="row" spacing={0.5} flexWrap="wrap">
                {displayed.map(c => (
                    <Chip key={c.category.id} label={c.category.name} size="small" variant="outlined" />
                ))}
                {remaining > 0 && (
                    <Chip label={`+${remaining} more tags`} size="small" variant="outlined" />
                )}
            </Stack>
        );
    };

    return (
        <React.Fragment>
            <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={toggleOpen}
                    >
                        {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{urlDetail.url.id}</TableCell>
                <TableCell>{urlDetail.url.url}</TableCell>
                <TableCell>
                    {renderCategories()}
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                            <Grid container spacing={2}>
                                <Grid size={7.2}> {/* 60% */}
                                    <Typography variant="h6" gutterBottom component="div">
                                        URL Category Mappings
                                    </Typography>
                                    <TextField
                                        size="small"
                                        placeholder="Search categories..."
                                        value={categorySearch}
                                        onChange={(e) => setCategorySearch(e.target.value)}
                                        sx={{ mb: 1, width: '100%' }}
                                    />
                                    <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 300 }}>
                                        <Table size="small" stickyHeader>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Category</TableCell>
                                                    <TableCell>Constraint</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {filteredMappings.map((m) => (
                                                    <TableRow key={m.category.id}>
                                                        <TableCell>{m.category.name}</TableCell>
                                                        <TableCell>{m.constraint?.comment || '-'}</TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </Grid>
                                <Grid size={4.8}> {/* 40% */}
                                    <Typography variant="h6" gutterBottom component="div">
                                        History
                                    </Typography>
                                    <HistoryTable commits={history} />
                                </Grid>
                            </Grid>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    )
});

function MatchingListPage() {
    const {currentBranch} = useBranch();
    // State info for the Page
    const [urls, setURLs] = React.useState<IRestURLDetail[]>([]);

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<IRestURLDetail[]>([]);
    const comparator = (a: IRestURLDetail, b: IRestURLDetail): number => a.url.url.localeCompare(b.url.url);
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

    // Load urls From backend
    React.useEffect(() => {
        getURLs(currentBranch)
            .then((urlsData) => {
                setURLs(urlsData);
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
                            <Table sx={{ minWidth: 650 }} size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell style={{ width: 40 }} />
                                        <TableCell>ID</TableCell>
                                        <TableCell>URL</TableCell>
                                        <TableCell>Categories</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(urlMap =>
                                        <BuildRow
                                            key={urlMap.url.id}
                                            urlDetail={urlMap}
                                            branch={currentBranch}
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

import React from 'react';
import {
    Box,
    Button,
    Collapse,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    IconButton,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField, Tooltip,
} from "@mui/material";
import Grid from '@mui/material/Grid2';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";

import {getCategories} from "../api/category";
import {
    createURL,
    deleteURL,
    getURLs,
    setURLCategory,
    updateURL,
} from "../api/url"
import {useAuth} from "../model/AuthContext";
import {ListHeader} from "./shared/ListHeader";
import {MyPaginator} from "./shared/MyPaginator";
import {buildLUTFromID, LUT} from "../model/types/LookUpTable";
import {TriState} from "../model/types/EditDialogState";
import {CategoryPicker} from "./shared/CategoryPicker";
import {simpleStringCheck, simpleURLCheck} from "../util/InputValidators";
import {BY_ID} from "../util/comparator";
import {SearchParser} from "../searchParser";
import {getHistory, ICommits} from "../api/history";
import HistoryTable from "./shared/HistoryTable";
import {KVaddRAW} from "../model/types/stringKV";
import {IUrl, IMutableUrl, UrlToKV, UrlFieldsRaw} from "../model/types/url";
import {ICategory} from "../model/types/category";

interface BuildRowProps {
    url: IUrl,
    updateURL: (newURL: IUrl) => void,
    categories: LUT<ICategory>,
    onEdit: (url: IUrl) => void,
    onDelete: (url: IUrl) => void,
    history: ICommits[],
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
    const { url, updateURL, categories, onEdit, onDelete, history } = props;
    const authMgmt = useAuth();

    // (un)fold a row into multiple rows
    const [isOpen, setIsOpen] = React.useState(false);

    // helper function, triggered when the category selector changes
    const handleChange = (newList: string[]) => {
        // update api
        setURLCategory(authMgmt.token, url.id, newList).then(newCats => {
            // save the new version
            const newURL = {...url, categories: newCats, pending_changes: true};
            updateURL(newURL);
        });
    };

    const myHist = React.useMemo(() => !isOpen ? [] : history.filter(h => h.ref_url.includes(url.id)), [history, isOpen, url.id])
    const bc_cat_time = url.bc_last_set ? new Date(url.bc_last_set * 1000).toLocaleString() : 'N/A';

    return (
        <React.Fragment>
            <TableRow key={url.id} sx={url.pending_changes ? { backgroundColor: (theme) => theme.palette.warning.light } : undefined}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{url.id}</TableCell>
                <TableCell>{url.hostname}</TableCell>
                <TableCell>
                    <CategoryPicker
                        isCategories={url.categories}
                        onChange={(newList) => handleChange(newList)}
                        categories={categories}
                    />
                </TableCell>
                <TableCell>{url.description}</TableCell>
                <TableCell>
                    <Tooltip title={`Updated ${bc_cat_time}`} placement="left" arrow>
                        <div>
                            {url.bc_cats.map((cat, index) => (
                                <div key={index}>{cat}</div>
                            ))}
                        </div>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <IconButton aria-label="edit url" onClick={() => onEdit(url)} size="small">
                        <EditIcon />
                    </IconButton>
                    <IconButton aria-label="delete url" onClick={() => onDelete(url)} size="small">
                        <DeleteIcon />
                    </IconButton>
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0}} colSpan={7}>
                    <Collapse in={isOpen} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1}} >
                            <HistoryTable commits={myHist} url={url.id} />
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    )
});

function MatchingListPage() {
    const authMgmt = useAuth();

    // State info for the Page
    const [urls, setURLs] = React.useState<IUrl[]>([]);
    const [categories, setCategory] = React.useState<LUT<ICategory>>({});
    const [history, setHistory] = React.useState<ICommits[]>([]);

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<IUrl[]>([]);
    const comparator = BY_ID;
    const [quickSearch, setQuickSearch] = React.useState<SearchParser | null>(null);
    // Memoize the filtered rows to avoid unnecessary recalculations
    const filteredRows = React.useMemo(
        () => urls.filter(x => {
            return quickSearch?.test(KVaddRAW(UrlToKV(x, categories))) ?? true;
        }),
        [quickSearch, urls, categories],
    );

    // Memoize the download rows to avoid unnecessary transformations
    const downloadRows = React.useMemo(
        () => filteredRows.map(row => UrlToKV(row, categories)),
        [filteredRows, categories],
    );

    // Load urls (& Categories) From backend
    React.useEffect(() => {
        Promise.all([getURLs(authMgmt.token), getCategories(authMgmt.token)])
            .then(([urlsData, categoriesData]) => {
                setURLs(urlsData);
                setCategory(buildLUTFromID(categoriesData));
                // fetch history async after urls and categories, since it's only needed when opening a row
                return getHistory(authMgmt.token);
            })
            .then(historyData => {
                setHistory(historyData);
            })
            .catch((error) => console.error("Error:", error));
    }, [authMgmt]);

    // Edit Dialog State
    const [editURL, setEditURL] = React.useState<TriState<IUrl>>(TriState.CLOSED);
    const handleEditOpen = React.useCallback((uri: IUrl | null = null) => {
        setEditURL(uri ? new TriState(uri) : TriState.NEW);
    }, [setEditURL]);
    const handleEditDialogClose = () => {
        setEditURL(TriState.CLOSED);
    };

    // create or edit a new object
    const handleSave = async (urlID: string|null, uri: IMutableUrl) => {
        if (urlID == null) {
            // add new URL
            const newURI = await createURL(authMgmt.token, uri);
            setURLs([...urls, newURI]);
        } else {
            const newURI = await updateURL(authMgmt.token, urlID, uri)
            // "replace" existing URL if id matches
            setURLs(urls.map(u => u.id === urlID ? newURI : u));
        }
        handleEditDialogClose();
    };

    const handleDelete = React.useCallback((remove_url: IUrl) => {
        deleteURL(authMgmt.token, remove_url.id).then(() => {
            // remove URL with ID from store
            setURLs(urls.filter(uri => uri.id !== remove_url.id));
        });
    }, [setURLs, authMgmt, urls]);

    // save an updated URL object in the urls cache
    const handleUpdateURL = React.useCallback((newURL: IUrl) =>
            setURLs(urls.map(u => u.id === newURL.id ? newURL : u)),
        [urls]
    );

    return (
        <>
            <Grid
                container
                spacing={1}
                justifyContent="center"
                alignItems="center"
            >
                <ListHeader
                    onCreate={handleEditOpen}
                    setQuickSearch={setQuickSearch}
                    addElement={"URL"}
                    downloadRows={downloadRows}
                    availableFields={UrlFieldsRaw}
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
                                        <TableCell></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(url =>
                                        <BuildRow
                                            key={url.id}
                                            url={url}
                                            updateURL={handleUpdateURL}
                                            categories={categories}
                                            onEdit={handleEditOpen}
                                            onDelete={handleDelete}
                                            history={history}
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
            <EditDialog
                uri={editURL}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

interface EditDialogProps {
    uri: TriState<IUrl>,
    onClose: () => void,
    onSave: (id: string | null, uri: IMutableUrl) => void
}
function EditDialog(props: EditDialogProps) {
    let {uri, onClose, onSave} = props;

    const [hostname, setHostname] = React.useState('');
    const [description, setDescription] = React.useState('');

    // validate inputs
    const hostnameError: string|null = React.useMemo(
        () => simpleURLCheck(hostname, true),
        [hostname],
    )
    const descriptionError: string|null = React.useMemo(
        () => simpleStringCheck(description),
        [description],
    )

    React.useEffect(() => {
        // set existing values if a category was provided
        // else force clear the fields
        if (!uri.isNull()) {
            setHostname(uri.getValue()!.hostname);
            setDescription(uri.getValue()!.description);
        } else {
            setHostname("")
            setDescription("");
        }
    }, [uri]);

    const handleSave = () => {
        if (hostnameError != null || descriptionError != null) {
            // only continue if the inputs are valid
            return;
        }

        onSave(uri.getValue()?.id ?? null, {hostname, description});
        setHostname("")
        setDescription("");
    };

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleSave();
        }
    };

    return (
        <Dialog open={uri.isOpen()} onClose={onClose} onKeyDown={handleKeyDown}>
            <DialogTitle>Edit URL</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                    <TextField
                        label="Hostname (FQDN)"
                        value={hostname}
                        onChange={(e) => setHostname(e.target.value)}
                        error={hostnameError != null}
                        helperText={hostnameError ? hostnameError : ''}
                        required
                    />
                    <TextField
                        label="Description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        error={descriptionError != null}
                        helperText={descriptionError ? descriptionError : ''}
                    />
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleSave}>Save</Button>
                <Button onClick={onClose}>Cancel</Button>
            </DialogActions>
        </Dialog>
    );
}

export default MatchingListPage;

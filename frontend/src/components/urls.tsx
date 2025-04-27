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
    TextField,
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
}
/**
 * Renders a table row for a URL entry.
 *
 * Wrapped in React.memo to prevent unnecessary re-renders in the URL table.
 * This works as long as none of the props passed to the Component change
 *
 * The caching also requires us to ensure that all callbacks passed are constants (e.g. wrapped in useCallable)
 */
const BuildRow = React.memo(function BuildRow(props: BuildRowProps) {
    const { url, updateURL, categories, onEdit, onDelete } = props;
    const authMgmt = useAuth();

    // (un)fold a row into multiple rows
    const [isOpen, setIsOpen] = React.useState(false);

    // helper function, triggered when the category selector changes
    const handleChange = (newList: string[]) => {
        // update api
        setURLCategory(authMgmt.token, url.id, newList).then(newCats => {
            // save the new version
            const newURL = {...url, categories: newCats};
            updateURL(newURL);
        });
    };

    const [myHist, setMyHist] = React.useState<ICommits[]>([]);
    React.useEffect(() => {
        if (!isOpen) return;
        getHistory(authMgmt.token).then(fullHist => {
            const newMyHist = fullHist.filter(h => h.ref_url.includes(url.id));
            setMyHist(newMyHist);
        });
    }, [isOpen, authMgmt, url])

    return (
        <React.Fragment>
            <TableRow key={url.id}>
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
                <TableCell>{url.bc_cats.map((cat, index) => (
                    <div key={index}>{cat}</div>
                ))}</TableCell>
                <TableCell>
                    <EditIcon onClick={() => onEdit(url)}/>
                    <DeleteIcon onClick={() => onDelete(url)}/>
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0}} colSpan={7}>
                    <Collapse in={isOpen} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1}} >
                            <HistoryTable commits={myHist} />
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

    return (
        <Dialog open={uri.isOpen()} onClose={onClose}>
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

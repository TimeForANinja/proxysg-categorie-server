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
    Typography,
} from "@mui/material";
import Grid from '@mui/material/Grid2';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import DeleteIcon from "@mui/icons-material/Delete";

import {getCategories, ICategory} from "../api/categories";
import {createURL, deleteURL, getURLs, IMutableURL, IURL, setURLCategory, updateURL} from "../api/urls"
import {useAuth} from "../model/AuthContext";
import {ListHeader} from "./shared/list-header";
import {MyPaginator} from "./shared/paginator";
import {buildLUTFromID, LUT} from "../util/LookUpTable";
import {TriState} from "./shared/EditDialogState";
import {CategoryPicker} from "./shared/CategoryPicker";

const COMPARATORS = {
    BY_ID:  (a: IURL, b: IURL) => a.id - b.id
};

interface BuildRowProps {
    url: IURL,
    updateURL: (newURL: IURL) => void,
    categories: LUT<ICategory>,
    onDelete: () => void,
}
function BuildRow(props: BuildRowProps) {
    const { url, updateURL, categories, onDelete } = props;
    const authMgmt = useAuth();

    // (un)fold a row into multiple rows
    const [isOpen, setIsOpen] = React.useState(false);

    // helper function, triggered when category selector changes
    const handleChange = (newList: number[]) => {
        // update api
        setURLCategory(authMgmt.token, url.id, newList).then(newCats => {
            // save new version
            const newURL = {...url, categories: newCats};
            updateURL(newURL);
        });
    };

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
                <TableCell><DeleteIcon onClick={onDelete}/></TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0}} colSpan={4}>
                    <Collapse in={isOpen} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1}} >
                            <Typography variant="h6" gutterBottom component="div">
                                History
                            </Typography>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    )
}

function MatchingListPage() {
    const authMgmt = useAuth();

    // State info for the Page
    const [urls, setURLs] = React.useState<IURL[]>([]);
    const [categories, setCategory] = React.useState<LUT<ICategory>>([]);

    // search & pagination
    const [visibleRows, setVisibleRows] = React.useState<IURL[]>([]);
    const comparator = COMPARATORS.BY_ID;
    const [quickSearch, setQuickSearch] = React.useState('');
    const filteredRows = React.useMemo(
        () =>
            urls.filter(x => {
                // TODO: not sure if switching to sth. like "levenshtein distance" makes more sense?
                const cat_str = x.categories.map(c => categories[c]?.name).join(' ');
                const search_str = `${x.id} ${x.hostname} ${cat_str}`;
                return search_str.toLowerCase().includes(quickSearch.toLowerCase());
            }),
        [quickSearch, urls, categories],
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
    const [editURL, setEditURL] = React.useState<TriState<IURL>>(TriState.CLOSED);
    const handleEditOpen = (uri: IURL | null = null) => {
        setEditURL(uri ? new TriState(uri) : TriState.NEW);
    };
    const handleEditDialogClose = () => {
        setEditURL(TriState.CLOSED);
    };

    // create or edit new object
    const handleSave = (urlID: number|null, uri: IMutableURL) => {
        if (urlID == null) {
            // add new URL
            createURL(authMgmt.token, uri).then(newURI => {
                setURLs([...urls, newURI]);
            });
        } else {
            updateURL(authMgmt.token, urlID, uri).then(newURI => {
                // "replace" existing URL if id matches
                setURLs(urls.map(u => u.id === urlID ? newURI : u));
            })
        }
        handleEditDialogClose();
    };

    const handleDelete = (remove_url: IURL) => {
        deleteURL(authMgmt.token, remove_url.id).then(() => {
            // remove URL with ID from store
            setURLs(urls.filter(uri => uri.id !== remove_url.id));
        });
    }

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
                />
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper} style={{maxHeight: '100%'}}>
                            <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell />
                                        <TableCell>ID</TableCell>
                                        <TableCell>Hostname</TableCell>
                                        <TableCell>Categories</TableCell>
                                        <TableCell></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(url =>
                                        <BuildRow
                                            key={url.id}
                                            url={url}
                                            updateURL={newURL => setURLs(urls.map(u => u.id === newURL.id ? newURL : u))}
                                            categories={categories}
                                            onDelete={() => handleDelete(url)}
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
    uri: TriState<IURL>,
    onClose: () => void,
    onSave: (id: number | null, uri: IMutableURL) => void
}
function EditDialog(props: EditDialogProps) {
    let {uri, onClose, onSave} = props;

    const [hostname, setHostname] = React.useState('');

    React.useEffect(() => {
        // set existing values if a category was provided
        // else force clear the fields
        if (!uri.isNull()) {
            setHostname(uri.getValue()!.hostname);
        } else {
            setHostname("")
        }
    }, [uri]);

    const handleSave = () => {
        onSave(uri.getValue()?.id ?? null, {hostname});
        setHostname("")
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

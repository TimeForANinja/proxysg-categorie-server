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
import EditIcon from "@mui/icons-material/Edit";

import {getCategories, ICategory} from "../api/categories";
import {createURL, deleteURL, getURLs, IMutableURL, IURL, setURLCategory, updateURL} from "../api/urls"
import {useAuth} from "../model/AuthContext";
import {ListHeader} from "./shared/list-header";
import {MyPaginator} from "./shared/paginator";
import {buildLUTFromID, LUT} from "../model/types/LookUpTable";
import {TriState} from "../model/types/EditDialogState";
import {CategoryPicker} from "./shared/CategoryPicker";
import {simpleStringCheck, simpleURLCheck} from "../util/InputValidators";
import {BY_ID} from "../util/comparator";
import {BuildSyntaxTree, TreeNode} from "../searchParser/Parser";

interface BuildRowProps {
    url: IURL,
    updateURL: (newURL: IURL) => void,
    categories: LUT<ICategory>,
    onEdit: () => void,
    onDelete: () => void,
}
function BuildRow(props: BuildRowProps) {
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
                    <EditIcon onClick={onEdit}/>
                    <DeleteIcon onClick={onDelete}/>
                </TableCell>
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
    const [categories, setCategory] = React.useState<LUT<ICategory>>({});

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<IURL[]>([]);
    const comparator = BY_ID;
    const [quickSearch, setQuickSearch] = React.useState('');
    const filteredRows = React.useMemo(
        () => {
            let tree: TreeNode | null = null;
            try {
                tree = BuildSyntaxTree(quickSearch);
                console.log("Search Query:", tree.print());
            } catch(e: Error | any) {
                console.log("Invalid Error:", e?.message, e?.stack);
            }
            return urls.filter(x => {
                const cat_str = x.categories.map(c => categories[c]?.name).join(' ');
                const bc_cat_str = x.bc_cats.join(' ');
                const search_str = `${x.id} ${x.hostname} ${x.description} ${bc_cat_str} ${cat_str}`;
                const raw_row = {
                    id: x.id,
                    host: x.hostname,
                    description: x.description,
                    cats: cat_str,
                    bc_cats: bc_cat_str,
                    _raw: search_str,
                }

                // test new parser
                return !!tree?.calc(raw_row);
            });
        },
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

    // create or edit a new object
    const handleSave = async (urlID: string|null, uri: IMutableURL) => {
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
                    downloadRows={filteredRows.map(row => ({
                        "id": row.id,
                        "hostname": row.hostname,
                        "description": row.description,
                        "cat_ids": row.categories.join(','),
                        "cats": row.categories.map(c => categories[c]?.name).join(','),
                        "bc_cats": row.bc_cats.join(','),
                    }))}
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
                                            updateURL={newURL => setURLs(urls.map(u => u.id === newURL.id ? newURL : u))}
                                            categories={categories}
                                            onEdit={() => handleEditOpen(url)}
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
    onSave: (id: string | null, uri: IMutableURL) => void
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

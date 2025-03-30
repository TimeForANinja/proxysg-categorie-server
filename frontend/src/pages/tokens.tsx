import React from 'react';
import {
    Alert,
    Box,
    Button,
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
} from '@mui/material';
import Grid from '@mui/material/Grid2'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check';
import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from "@mui/icons-material/Edit"
import ShuffleIcon from "@mui/icons-material/Shuffle";

import {
    createToken,
    deleteToken,
    getAPITokens,
    IApiToken,
    IMutableApiToken,
    rotateToken,
    setTokenCategory,
    updateToken
} from "../api/tokens";
import {getCategories, ICategory} from "../api/categories";
import {useAuth} from "../model/AuthContext";
import {ListHeader} from "./shared/list-header";
import {ConfirmDeletionDialog} from "./shared/ConfirmDeletionDialog";
import {TriState} from "./shared/EditDialogState";
import {MyPaginator} from "./shared/paginator";
import {buildLUTFromID, LUT} from "../util/LookUpTable";
import {CategoryPicker} from "./shared/CategoryPicker02";

const COMPARATORS = {
    BY_ID:  (a: IApiToken, b: IApiToken) => a.id - b.id
};

const TIME_SECONDS = 1000;

const parse_last_used = (last_use: number) => {
    if (last_use === 0) {
        return 'never';
    } else {
        return new Date(last_use * TIME_SECONDS).toLocaleString();
    }
}

interface BuildRowProps {
    token: IApiToken,
    categories: LUT<ICategory>,
    onEdit: () => void,
    onShuffle: () => void,
    onDelete: () => void,
}
function BuildRow(props: BuildRowProps) {
    const {
        token,
        categories,
        onEdit,
        onDelete,
        onShuffle,
    } = props;
    const authMgmt = useAuth();

    // toggle the visibility of the token
    const [hideToken, setHideToken] = React.useState(false);

    const [isCategories, setCategories] = React.useState(token.categories);

    // tracks state for the copy icon, which slightly changes for a few seconds after being pressed
    const [isCopied, setIsCopied] = React.useState(false);
    // helper function, triggered when the "copy" button is pressed
    const handleCopy = async () => {
        // copy ID to clipboard
        await navigator.clipboard.writeText(token.token);

        // Change the look of the icon for a few seconds
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 1.5 * TIME_SECONDS);
    };

    // helper function, triggered when category selector changes
    const handleChange = (newList: number[]) => {
        // update api
        setTokenCategory(authMgmt.token, token.id, newList).then(newCats => {
            // save new version
            setCategories(newCats);
        });
    };

    return (
        <TableRow
            key={token.id}
            sx={{ '&:last-child td, &:last-child th': {border: 0 }}}
        >
            <TableCell component="th" scope="row">{token.id}</TableCell>
            <TableCell>{token.description}</TableCell>
            <TableCell align="right">
                {hideToken ? token.token : token.token.replace(/[a-zA-Z0-9]/g, '*')}
                <IconButton onClick={() => setHideToken(!hideToken)}>
                    { hideToken ? <VisibilityIcon /> : <VisibilityOffIcon /> }
                </IconButton>
                <IconButton onClick={onShuffle}>
                    <ShuffleIcon />
                </IconButton>
                <IconButton onClick={handleCopy}>
                    {isCopied ? <CheckIcon /> : <ContentCopyIcon />}
                </IconButton>
            </TableCell>
            <TableCell>{ parse_last_used(token.last_use) }</TableCell>
            <TableCell align="right">
                <CategoryPicker
                    onChange={(newList) => handleChange(newList)}
                    categories={categories}
                    isCategories={isCategories}
                />
            </TableCell>
            <TableCell>
                <EditIcon onClick={onEdit} />
                <DeleteIcon onClick={onDelete}/>
            </TableCell>
        </TableRow>
    )
}

function ApiTokenPage() {
    const authMgmt = useAuth();

    // State info for the Page
    const [tokens, setTokens] = React.useState<IApiToken[]>([]);
    const [categories, setCategory] = React.useState<LUT<ICategory>>([]);

    // search & pagination
    const [visibleRows, setVisibleRows] = React.useState<IApiToken[]>([]);
    const comparator = COMPARATORS.BY_ID;
    const [quickSearch, setQuickSearch] = React.useState('');
    const filteredRows = React.useMemo(
        () =>
            tokens.filter(x => {
                // TODO: not sure if switching to sth. like "levenshtein distance" makes more sense?
                const cat_str = x.categories.map(c => categories[c]?.name).join(' ');
                const search_str = `${x.id} ${x.description} ${parse_last_used(x.last_use)} ${cat_str}`.toLowerCase();
                return search_str.toLowerCase().includes(quickSearch.toLowerCase());
            }),
        [quickSearch, tokens, categories],
    );

    // Track object (if any) for which a delete confirmation is open
    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<IApiToken | null>(null);

    // Load tokens (& Categories) From backend
    React.useEffect(() => {
        Promise.all([ getAPITokens(authMgmt.token), getCategories(authMgmt.token)])
            .then(([tokenData, categoryData]) => {
                setTokens(tokenData);
                setCategory(buildLUTFromID(categoryData))
            })
            .catch((error) => console.error("Error:", error));
    }, [authMgmt]);

    // Edit Dialog State
    const [editToken, setEditToken] = React.useState<TriState<IApiToken>>(TriState.CLOSED);
    const handleEditOpen = (token: IApiToken | null = null) => {
        setEditToken(token ? new TriState(token) : TriState.NEW);
    };
    const handleEditDialogClose = () => {
        setEditToken(TriState.CLOSED);
    };

    // create or edit new object
    const handleSave = (tokenID: number|null, token: IMutableApiToken) => {
        if (tokenID == null) {
            // add new token
            createToken(authMgmt.token, token).then(newTok => {
                setTokens([...tokens, newTok]);
            });
         } else {
            updateToken(authMgmt.token, tokenID, token).then(newTok => {
                // "replace" existing token if id matches
                setTokens(tokens.map(tok => tok.id === tokenID ? newTok : tok));
            })
        }
        handleEditDialogClose();
    };

    const handleDelete = (token: IApiToken) => {
        // show the dialogue to confirm the deletion
        setDeleteDialogOpen(token);
    }
    const handleDeleteConfirmation = (del: boolean) => {
        // del == true means the user confirmed the popup
        if (del && isDeleteDialogOpen != null) {
            deleteToken(authMgmt.token, isDeleteDialogOpen.id).then(() => {
                // remove token with ID from store
                setTokens(tokens.filter(tok => tok.id !== isDeleteDialogOpen.id));
            });
        }
        setDeleteDialogOpen(null);
    }

    // generate a new token
    const handleOnShuffle = (token: IApiToken) => {
        rotateToken(authMgmt.token, token.id).then(newTok => {
            // "replace" existing token if id matches
            setTokens(tokens.map(tok => tok.id === token.id ? newTok : tok));
        })
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
                    addElement={"Token"}
                />
                <Grid size={12}>
                    <Alert severity="info">You can use Tokens by sending a request to "/api/compile/&lt;token&gt;"</Alert>
                </Grid>
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 650 }} size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell component="th" scope="row">ID</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell align="right">Token</TableCell>
                                        <TableCell>Last Used</TableCell>
                                        <TableCell align="right">Categories</TableCell>
                                        <TableCell></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(token =>
                                        <BuildRow
                                            key={token.id}
                                            token={token}
                                            categories={categories}
                                            onEdit={() => handleEditOpen(token)}
                                            onShuffle={() => handleOnShuffle(token)}
                                            onDelete={() => handleDelete(token)}
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
            <ConfirmDeletionDialog
                onConfirmation={handleDeleteConfirmation}
                header={"Delete API Token?"}
                body={"Are you sure you want to Delete the API Token permanently?"}
                isOpen={isDeleteDialogOpen != null}
            />
            <EditDialog
                token={editToken}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

interface EditDialogProps {
    token: TriState<IApiToken>,
    onClose: () => void,
    onSave: (id: number | null, token: IMutableApiToken) => void
}
function EditDialog(props: EditDialogProps) {
    const { token, onClose, onSave } = props;

    const [description, setDescription] = React.useState('');

    React.useEffect(() => {
        // set existing values if a category was provided
        // else force clear the fields
        if (!token.isNull()) {
            setDescription(token.getValue()!.description);
        } else {
            setDescription("");
        }
    }, [token]);

    const handleSave = () => {
        onSave(token.getValue()?.id ?? null, { description });
    };

    return (
        <Dialog open={token.isOpen()} onClose={onClose}>
            <DialogTitle>Edit API Token</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                    <TextField
                        label="Description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
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

export default ApiTokenPage;

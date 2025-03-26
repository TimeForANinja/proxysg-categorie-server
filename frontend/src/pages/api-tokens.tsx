import React from 'react';
import {
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Button,
    TextField,
    DialogContentText,
    Alert
} from '@mui/material';
import {
    createToken,
    getAPITokens,
    updateToken,
    rotateToken,
    deleteToken,
    IApiToken,
    IMutableApiToken,
    setTokenCategory
} from "../api/tokens";
import {getCategories, ICategory} from "../api/categories";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import IconButton from '@mui/material/IconButton';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check';
import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from "@mui/icons-material/Edit"
import ShuffleIcon from "@mui/icons-material/Shuffle";
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from "@mui/material/MenuItem";
import Box from "@mui/material/Box";

const TIME_SECONDS = 1000;

function BuildRow(props: {
    token: IApiToken,
    categories: ICategory[],
    onEdit: () => void,
    onShuffle: () => void,
    onDelete: () => void,
}) {
    const {
        token,
        categories,
        onEdit,
        onDelete,
        onShuffle,
    } = props;
    // tracks state for the copy icon, which slightly changes for a few seconds after being pressed
    const [isCopied, setIsCopied] = React.useState(false);
    // toggle the visibility of the token
    const [hideToken, setHideToken] = React.useState(false);

    const [isCategories, setCategories] = React.useState(token.categories);

    // helper function, triggered when the "copy" button is pressed
    const handleCopy = async () => {
        // copy ID to clipboard
        await navigator.clipboard.writeText(token.token);

        // Change the look of the icon for a few seconds
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 1.5 * TIME_SECONDS);
    };

    // helper function, triggered when category selector changes
    const handleChange = (event: SelectChangeEvent<number[]>) => {
        if (Array.isArray(event.target.value)) {
            // update api
            setTokenCategory(token.id, event.target.value).then(newCats => {
                // save new version
                setCategories(newCats);
            });
            /* old version
            const { added, removed } = CompareLists(isCategories, event.target.value);

            added.forEach(cat => addTokenCategory(token.id, cat));
            removed.forEach(cat => deleteTokenCategory(token.id, cat));

            setCategories(event.target.value);
            */
        }
    };

    const last_use_time = token.last_use === 0 ? 'never' : new Date(token.last_use * 1000).toLocaleString();

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
                <TableCell>{ last_use_time }</TableCell>
                <TableCell align="right">
                    <Select
                        multiple
                        value={isCategories}
                        label="Categories"
                        onChange={handleChange}
                        displayEmpty
                        renderValue={(selected) => selected.map(c => categories.find(cat => cat.id === c)?.name).join(', ')}
                    >
                        {
                            categories.map((cat, catIDX) => {
                                return (
                                    <MenuItem key={catIDX} value={cat.id}>
                                        <div style={{ background: cat.color}}>{cat.name}</div>
                                    </MenuItem>
                                )
                            })
                        }
                    </Select>
                </TableCell>
                <TableCell>
                    <EditIcon onClick={onEdit} />
                    <DeleteIcon onClick={onDelete}/>
                </TableCell>
            </TableRow>
    )
}

function ApiTokenPage() {
    const [tokens, setTokens] = React.useState<IApiToken[]>([]);
    const [categories, setCategory] = React.useState<ICategory[]>([]);
    const [editToken, setEditToken] = React.useState<IApiToken | null>(null);
    const [isEditDialogOpen, setEditDialogOpen] = React.useState(false);
    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<IApiToken | null>(null);

    // Load tokens (& Categories) From backend
    React.useEffect(() => {
        Promise.all([ getCategories(), getAPITokens()])
            .then(([categoryData, tokenData]) => {
                setTokens(tokenData);
                setCategory(categoryData)
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    const handleEditOpen = (token: IApiToken | null) => {
        setEditToken(token);
        setEditDialogOpen(true);
    };

    const handleEditDialogClose = () => {
        setEditDialogOpen(false);
    };

    const handleSave = (tokenID: number|null, token: IMutableApiToken) => {
        if (tokenID == null) {
            // add new token
            createToken(token).then(newTok => {
                setTokens([...tokens, newTok]);
            });
         } else {
            updateToken(tokenID, token).then(newTok => {
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
            deleteToken(isDeleteDialogOpen.id).then(() => {
                // remove token with ID from store
                setTokens(tokens.filter(tok => tok.id !== isDeleteDialogOpen.id));
            });
        }
        setDeleteDialogOpen(null);
    }

    const handleOnShuffle = (token: IApiToken) => {
        rotateToken(token.id).then(newTok => {
            // "replace" existing token if id matches
            setTokens(tokens.map(tok => tok.id === token.id ? newTok : tok));
        })
    }

    return (
        <>
            <Dialog
                open={isDeleteDialogOpen != null}
                onClose={() => handleDeleteConfirmation(false)}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    {"Delete API Token?"}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        Are you sure you want to Delete the API Token?
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => handleDeleteConfirmation(false)}>Disagree</Button>
                    <Button onClick={() => handleDeleteConfirmation(true)} autoFocus>
                        Agree
                    </Button>
                </DialogActions>
            </Dialog>
            <Alert severity="info">You can use Tokens by sending a request to "/api/compile/&lt;token&gt;"</Alert>
            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
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
                        {tokens.map(token =>
                            <BuildRow
                                key={token.id}
                                token={token}
                                categories={categories}
                                onEdit={() => handleEditOpen(token)}
                                onShuffle={() => handleOnShuffle(token)}
                                onDelete={() => handleDelete(token)}
                            />
                        )}
                        <TableRow>
                            <TableCell colSpan={5} align="center">
                                <Button onClick={() => handleEditOpen(null)}>
                                    + Add Token
                                </Button>
                            </TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableContainer>
            <EditDialog
                isOpen={isEditDialogOpen}
                token={editToken}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

function EditDialog(props: {
    isOpen: boolean,
    token: IApiToken | null,
    onClose: () => void,
    onSave: (id: number | null, token: IMutableApiToken) => void
}) {
    const { isOpen, token, onClose, onSave } = props;

    const [description, setDescription] = React.useState('');

    React.useEffect(() => {
        if (token) {
            setDescription(token.description);
        } else {
            setDescription("");
        }
    }, [token]);

    const handleSave = () => {
        onSave(token?.id ?? null, { description });
    };

    return (
        <Dialog open={isOpen} onClose={onClose}>
            <DialogTitle>Edit API Token</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                    <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
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

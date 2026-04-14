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
import Grid from '@mui/material/Grid'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check';
import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from "@mui/icons-material/Edit"

import RefreshIcon from "@mui/icons-material/Refresh"

import {addTokenCategory, createToken, deleteToken, deleteTokenCategory, getTokens, rollToken} from "../api/token";
import {getCategories} from "../api/category";
import {ListHeader} from "./shared/ListHeader";
import {ConfirmDeletionDialog} from "./shared/ConfirmDeletionDialog";
import {TriState} from "../types/EditDialogState";
import {MyPaginator} from "./shared/MyPaginator";
import {buildLUTFromID, LUT} from "../types/LookUpTable";
import {CategoryPicker} from "./shared/CategoryPicker";
import {simpleStringCheck} from "../util/InputValidators";
import {SearchParser} from "../searchParser";
import {
    IApiToken,
    IMutableApiToken,
    ApiTokenToKV,
    ApiTokenFieldsRaw,
    IRestTokenDetail
} from '../types/apiToken';
import {ICategory} from "../types/category";
import {KVaddRAW} from "../types/stringKV";
import {useBranch} from "../hooks/useBranch";

const TIME_SECONDS = 1000;

interface BuildRowProps {
    tokenDetail: IRestTokenDetail,
    categories: LUT<ICategory>,
    onEdit: (token: IApiToken) => void,
    onDelete: (token: IApiToken) => void,
    onRoll: (token: IApiToken) => void,
    branch: string,
}
/**
 * Renders a table row for an ApiToken entry.
 *
 * Wrapped in React.memo to prevent unnecessary re-renders in the ApiToken table.
 * This works as long as none of the props passed to the Component change
 *
 * The caching also requires us to ensure that all callbacks passed are constants (e.g., wrapped in useCallable)
 */
const BuildRow = React.memo(function BuildRow(props: BuildRowProps) {
    const {
        tokenDetail,
        categories,
        onEdit,
        onDelete,
        onRoll,
        branch,
    } = props;

    const token = tokenDetail.token;

    // toggle the visibility of the token
    const [hideToken, setHideToken] = React.useState(false);

    // tracks state for the copy icon, which slightly changes for a few seconds after being pressed
    const [isCopied, setIsCopied] = React.useState(false);
    // helper function, triggered when the "copy" button is pressed
    const handleCopy = async () => {
        // copy ID to clipboard
        await navigator.clipboard.writeText(token.token_value);

        // Change the look of the icon for a few seconds
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 1.5 * TIME_SECONDS);
    };

    const handleChange = (newCats: string[], added: string[], removed: string[]) => {
        const tasks = []
        for (const a of added) {
            tasks.push(addTokenCategory(branch, token.id, a))
        }
        for (const r of removed) {
            tasks.push(deleteTokenCategory(branch, token.id, r))
        }
        Promise.all(tasks)
    }

    return (
        <TableRow
            key={token.id}
            sx={{
                '&:last-child td, &:last-child th': { border: 0 },
            }}
        >
            <TableCell component="th" scope="row">{token.id}</TableCell>
            <TableCell>{token.description}</TableCell>
            <TableCell align="right">
                {hideToken ? token.token_value : token.token_value.replace(/[a-zA-Z0-9]/g, '*')}
                <IconButton onClick={() => setHideToken(!hideToken)} size="small">
                    { hideToken ? <VisibilityIcon fontSize="small" /> : <VisibilityOffIcon fontSize="small" /> }
                </IconButton>
                <IconButton onClick={handleCopy} size="small">
                    {isCopied ? <CheckIcon fontSize="small" /> : <ContentCopyIcon fontSize="small" />}
                </IconButton>
                <IconButton onClick={() => onRoll(token)} size="small" title="Roll Token">
                    <RefreshIcon fontSize="small" />
                </IconButton>
            </TableCell>
            <TableCell align="right">
                <CategoryPicker
                    onChange={handleChange}
                    categories={categories}
                    isCategories={tokenDetail.categories}
                />
            </TableCell>
            <TableCell>
                <IconButton aria-label="edit token" onClick={() => onEdit(token)} size="small">
                    <EditIcon />
                </IconButton>
                <IconButton aria-label="delete token" onClick={() => onDelete(token)} size="small">
                    <DeleteIcon />
                </IconButton>
            </TableCell>
        </TableRow>
    )
});

function ApiTokenPage() {
    const { currentBranch } = useBranch();
    // State info for the Page
    const [tokens, setTokens] = React.useState<IRestTokenDetail[]>([]);
    const [categories, setCategory] = React.useState<LUT<ICategory>>({});

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<IRestTokenDetail[]>([]);
    const comparator = React.useCallback((a: IRestTokenDetail, b: IRestTokenDetail) => a.token.id.localeCompare(b.token.id), []);
    const [quickSearch, setQuickSearch] = React.useState<SearchParser | null>(null);
    // Memoize the filtered rows to avoid unnecessary recalculations
    const filteredRows = React.useMemo(
        () => tokens.filter(x => {
            return quickSearch?.test(KVaddRAW(ApiTokenToKV(x))) ?? true;
        }),
        [quickSearch, tokens],
    );

    // Memoize the download rows to avoid unnecessary transformations
    const downloadRows = React.useMemo(
        () => filteredRows.map(row => ApiTokenToKV(row)),
        [filteredRows],
    );

    // Track the object (if any) for which a delete confirmation is open
    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<IApiToken | null>(null);

    // Load tokens (& Categories) From backend
    const fetchData = React.useCallback(() => {
        Promise.all([ getTokens(currentBranch), getCategories(currentBranch)])
            .then(([tokenData, categoryData]) => {
                setTokens(tokenData);
                setCategory(buildLUTFromID(categoryData))
            })
            .catch((error) => console.error("Error:", error));
    }, [currentBranch]);

    React.useEffect(() => {
        fetchData();
    }, []);

    // Edit Dialog State
    const [editToken, setEditToken] = React.useState<TriState<IApiToken>>(TriState.CLOSED);
    const handleEditOpen = React.useCallback((token: IApiToken | null = null) => {
        setEditToken(token ? new TriState(token) : TriState.NEW);
    }, []);
    const handleEditDialogClose = () => {
        setEditToken(TriState.CLOSED);
    };

    // create or edit a new object
    const handleSave = async (tokenID: string|null, token: IMutableApiToken) => {
        if (tokenID == null) {
            // add new token
            await createToken(currentBranch, token)
            fetchData();
         }
        handleEditDialogClose();
    };

    const handleDelete = React.useCallback((token: IApiToken) => {
        // show the dialogue to confirm the deletion
        setDeleteDialogOpen(token);
    }, []);
    const handleDeleteConfirmation = (del: boolean) => {
        // del == true means the user confirmed the popup
        if (del && isDeleteDialogOpen != null) {
            deleteToken(currentBranch, isDeleteDialogOpen.id).then(() => {
                // refresh the list
                fetchData();
            });
        }
        setDeleteDialogOpen(null);
    }

    const handleRoll = React.useCallback((token: IApiToken) => {
        rollToken(currentBranch, token.id).then(() => {
            fetchData();
        }).catch((error) => console.error("Error rolling token:", error));
    }, [currentBranch, fetchData]);

    return (
        <>
            <Grid
                container
                spacing={1}
                sx={{ justifyContent: "center", alignItems: "center" }}
            >
                <ListHeader
                    onCreate={handleEditOpen}
                    setQuickSearch={setQuickSearch}
                    addElement={"Token"}
                    downloadRows={downloadRows}
                    availableFields={ApiTokenFieldsRaw}
                />
                <Grid size={12}>
                    <Alert severity="info">You can use Tokens by sending a request to "/api/compile/&lt;token&gt;"</Alert>
                </Grid>
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper} style={{maxHeight: 'calc(100vh - 190px)', overflow: 'auto'}}>
                            <Table sx={{ minWidth: 650 }} size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell component="th" scope="row">ID</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell align="right">Token</TableCell>
                                        <TableCell align="right">Categories</TableCell>
                                        <TableCell></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(detail =>
                                        <BuildRow
                                            key={detail.token.id}
                                            tokenDetail={detail}
                                            categories={categories}
                                            onEdit={handleEditOpen}
                                            onDelete={() => handleDelete(detail.token)}
                                            onRoll={handleRoll}
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
    onSave: (id: string | null, token: IMutableApiToken) => void
}
function EditDialog(props: EditDialogProps) {
    const { token, onClose, onSave } = props;

    const [description, setDescription] = React.useState('');

    // validate inputs
    const descriptionError: string|null = React.useMemo(
        () => simpleStringCheck(description),
        [description],
    )

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
        if (descriptionError != null) {
            // only continue if the inputs are valid
            return;
        }

        onSave(token.getValue()?.id ?? null, { description });
        setDescription("");
    };

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleSave();
        }
    };

    return (
        <Dialog open={token.isOpen()} onClose={onClose} onKeyDown={handleKeyDown}>
            <DialogTitle>Edit API Token</DialogTitle>
            <DialogContent>
                <Box component="div" sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
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

export default ApiTokenPage;

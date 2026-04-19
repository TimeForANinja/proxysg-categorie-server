import React from 'react';
import {
    Box,
    Button,
    Collapse,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
    IconButton,
    Tooltip,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import SearchIcon from "@mui/icons-material/Search";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { useNavigate } from "react-router-dom";

import {
    createCategory,
    deleteCategory,
    getCategories,
    updateCategory,
} from "../api/category";
import { getHistory } from "../api/history";
import {ListHeader} from "./shared/ListHeader";
import {ConfirmDeletionDialog} from "./shared/ConfirmDeletionDialog";
import {TriState} from "../types/EditDialogState";
import {MyPaginator} from "./shared/MyPaginator";
import {buildLUTFromID, filterLUT, getLUTValues, LUT, pushLUT} from "../types/LookUpTable";
import {simpleNameCheck} from "../util/InputValidators";
import {BY_ID} from "../util/comparator";
import {SearchParser} from "../searchParser";
import {CategoryFieldsRaw, CategoryToKV, ICategory, ICategoryCreateInput, ICategoryUpdateInput} from "../types/category";
import {IRestCommit} from "../types/history";
import {KVaddRAW} from "../types/stringKV";
import {useBranch} from "../hooks/useBranch";
import HistoryTable from "./shared/HistoryTable";
import {useAuth} from "../hooks/useLogin";
import { colorLUT, getForegroundColor } from '../util/colormixer';

interface BuildRowProps {
    category: ICategory,
    onEdit: (cat: ICategory) => void,
    onDelete: (cat: ICategory) => void,
    isLocked: boolean,
    branch: string,
}
/**
 * Renders a table row for a Category entry.
 *
 * Wrapped in React.memo to prevent unnecessary re-renders in the Category table.
 * This works as long as none of the props passed to the Component change
 *
 * The caching also requires us to ensure that all callbacks passed are constants (e.g., wrapped in useCallable)
 */
const BuildRow = React.memo(function BuildRow(props: BuildRowProps) {
    const {
        category,
        onEdit,
        onDelete,
        isLocked,
        branch,
    } = props;
    const authMgmt = useAuth();
    const navigate = useNavigate();

    const [open, setOpen] = React.useState(false);
    const [history, setHistory] = React.useState<IRestCommit[]>([]);

    const handleSearchInUrls = () => {
        // Build a wildcard search against the URL list by categories name
        // Escape special characters that could break the quoted value
        const safeName = category.name.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
        const query = `categories="*${safeName}*"`;
        const params = new URLSearchParams({ q: query });
        navigate({ pathname: '/url', search: `?${params.toString()}` });
    };

    const toggleOpen = () => {
        if (!open && history.length === 0) {
            getHistory(authMgmt.token, branch, [category.id])
                .then(setHistory)
                .catch(err => console.error('Failed to load history:', err));
        }
        setOpen(prev => !prev);
    };

    return (
        <React.Fragment>
            <TableRow key={category.id} sx={{ '& > *': { borderBottom: 'unset' } }}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={toggleOpen}
                    >
                        {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{category.id}</TableCell>
                <TableCell>{category.name}</TableCell>
                <TableCell>{category.description}</TableCell>
                <TableCell>
                    <Box sx={{
                        width: 24,
                        height: 24,
                        bgcolor: `#${category.color.toString(16).padStart(6, '0')}`,
                        border: '1px solid grey',
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: getForegroundColor(`#${category.color.toString(16).padStart(6, '0')}`),
                        fontSize: '10px',
                        fontWeight: 'bold'
                    }} />
                </TableCell>
                <TableCell align="right">
                    <IconButton aria-label="search URLs with this category" onClick={handleSearchInUrls} size="small">
                        <SearchIcon />
                    </IconButton>
                    {!isLocked && (
                        <>
                            <IconButton aria-label="edit category" onClick={() => onEdit(category)} size="small">
                                <EditIcon />
                            </IconButton>
                            <IconButton aria-label="delete category" onClick={() => onDelete(category)} size="small">
                                <DeleteIcon />
                            </IconButton>
                        </>
                    )}
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                            <HistoryTable commits={history} />
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    );
});

function CategoriesPage() {
    const authMgmt = useAuth();
    const { currentBranch, isLocked } = useBranch();
    // State info for the Page
    const [categories, setCategory] = React.useState<LUT<ICategory>>({});

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<ICategory[]>([]);
    const comparator = BY_ID;
    const [quickSearch, setQuickSearch] = React.useState<SearchParser | null>(null);
    // Memoize the filtered rows to avoid unnecessary recalculations
    const filteredRows = React.useMemo(
        () => getLUTValues(categories).filter(x => {
            return quickSearch?.test(KVaddRAW(CategoryToKV(x))) ?? true;
        }),
        [quickSearch, categories],
    );

    // Memoize the download rows to avoid unnecessary transformations
    const downloadRows = React.useMemo(
        () => filteredRows.map(row => CategoryToKV(row)),
        [filteredRows],
    );

    // Track the object (if any) for which a delete confirmation is open
    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<ICategory | null>(null);

    // load categories from the backend
    React.useEffect(() => {
        Promise.all([getCategories(authMgmt.token, currentBranch)])
            .then(([categoriesData]) => {
                setCategory(buildLUTFromID(categoriesData));
            })
            .catch((error) => console.error("Error:", error));
    }, [currentBranch]);

    // Edit Dialog State
    const [editCategory, setEditCategory] = React.useState<TriState<ICategory>>(TriState.CLOSED);
    const handleEditOpen = React.useCallback((category: ICategory | null = null) => {
        setEditCategory(category ? new TriState(category) : TriState.NEW);
    }, []);
    const handleEditDialogClose = React.useCallback(() => {
        setEditCategory(TriState.CLOSED);
    }, []);

    // create or edit a new object
    const handleSave = async (catID: string | null, category: ICategoryCreateInput | ICategoryUpdateInput) => {
        if (catID == null) {
            // add the new category
            const newCat = await createCategory(authMgmt.token, category as ICategoryCreateInput);
            setCategory(pushLUT(categories, newCat));
        } else {
            // update existing category
            const updatedCat = await updateCategory(authMgmt.token, catID, category as ICategoryUpdateInput);
            setCategory(pushLUT(categories, updatedCat));
        }
        handleEditDialogClose();
    };

    const handleDelete = React.useCallback((category: ICategory) => {
        // show the dialogue to confirm the deletion
        setDeleteDialogOpen(category);
    }, []);

    const handleDeleteConfirmation = async (del: boolean) => {
        // del == true means the user confirmed the popup
        if (del && isDeleteDialogOpen != null) {
            await deleteCategory(authMgmt.token, isDeleteDialogOpen.id);
            // remove category with ID from the store
            setCategory(filterLUT(categories, (cat => cat.id !== isDeleteDialogOpen.id)));
        }
        setDeleteDialogOpen(null);
    };

    return (
        <>
            <Grid
                container
                spacing={1}
                sx={{ justifyContent: "center" }}
            >
                <Grid size={12}>
                    <ListHeader
                        onCreate={handleEditOpen}
                        setQuickSearch={setQuickSearch}
                        addElement={"Category"}
                        downloadRows={downloadRows}
                        availableFields={CategoryFieldsRaw}
                        isLocked={isLocked}
                    />
                </Grid>
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper} style={{maxHeight: 'calc(100vh - 190px)', overflow: 'auto'}}>
                            <Table sx={{minWidth: 650}} size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell style={{ width: 40 }} />
                                        <TableCell component="th" scope="row">ID</TableCell>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell>Color</TableCell>
                                        <TableCell align="right"></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(cat =>
                                        <BuildRow
                                            key={cat.id}
                                            category={cat}
                                            onEdit={handleEditOpen}
                                            onDelete={handleDelete}
                                            isLocked={isLocked}
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
                header={"Delete Category?"}
                body={"Are you sure you want to Delete the Category? This will also unassign the Category from all URLs."}
                isOpen={isDeleteDialogOpen != null}
            />
            <EditDialog
                category={editCategory}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

interface EditDialogProps {
    category: TriState<ICategory>,
    onClose: () => void,
    onSave: (id: string | null, category: ICategoryCreateInput | ICategoryUpdateInput) => void
}
function EditDialog(props: EditDialogProps) {
    let {category, onClose, onSave} = props;

    const [name, setName] = React.useState('');
    const [description, setDescription] = React.useState('');
    const [color, setColor] = React.useState<number>(0);

    // validate inputs
    const nameError: string|null = React.useMemo(
        () => simpleNameCheck(name, true),
        [name],
    )

    React.useEffect(() => {
        // set existing values if a category was provided
        // else force clear the fields
        if (!category.isNull()) {
            setName(category.getValue()!.name);
            setDescription(category.getValue()!.description);
            setColor(category.getValue()!.color);
        } else {
            setName("");
            setDescription("");
            setColor(0);
        }
    }, [category]);

    const handleSave = () => {
        if (nameError != null) {
            // only continue if the inputs are valid
            return;
        }

        onSave(category.getValue()?.id ?? null, {name, description, color});
        setName("");
        setDescription("");
        setColor(0);
    };

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleSave();
        }
    };

    return (
        <Dialog open={category.isOpen()} onClose={onClose} onKeyDown={handleKeyDown}>
            <DialogTitle>{category.isNew() ? "Create Category" : "Edit Category"}</DialogTitle>
            <DialogContent>
                <Box component="div" sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
                    <TextField
                        label="Name"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        error={nameError != null}
                        helperText={nameError ? nameError : ''}
                        required
                        fullWidth
                    />
                    <TextField
                        label="Description"
                        value={description}
                        onChange={e => setDescription(e.target.value)}
                        required
                        fullWidth
                        multiline
                        rows={2}
                    />
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        <Typography variant="caption" color="text.secondary">Quick Color Selection</Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                            {Object.entries(colorLUT).map(([id, profile]) => (
                                <Tooltip key={id} title={profile.name}>
                                    <Box
                                        onClick={() => setColor(parseInt(profile.bg.replace('#', ''), 16))}
                                        sx={{
                                            width: 32,
                                            height: 32,
                                            bgcolor: profile.bg,
                                            borderRadius: '50%',
                                            cursor: 'pointer',
                                            border: color === parseInt(profile.bg.replace('#', ''), 16) ? '3px solid black' : '1px solid grey',
                                            '&:hover': {
                                                opacity: 0.8,
                                                transform: 'scale(1.1)'
                                            },
                                            transition: 'transform 0.1s'
                                        }}
                                    />
                                </Tooltip>
                            ))}
                        </Box>
                        <Typography variant="caption" color="text.secondary">Custom Color</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <input
                                id="category-color-picker"
                                type="color"
                                value={`#${color.toString(16).padStart(6, '0')}`}
                                onChange={e => setColor(parseInt(e.target.value.replace('#', ''), 16))}
                                style={{
                                    width: '60px',
                                    height: '60px',
                                    padding: 0,
                                    border: '1px solid rgba(0, 0, 0, 0.23)',
                                    borderRadius: '4px',
                                    background: 'none',
                                    cursor: 'pointer'
                                }}
                            />
                            <TextField
                                value={`#${color.toString(16).padStart(6, '0').toUpperCase()}`}
                                onChange={e => {
                                    const val = e.target.value.replace('#', '');
                                    if (/^[0-9A-Fa-f]{0,6}$/.test(val)) {
                                        setColor(parseInt(val || '0', 16));
                                    }
                                }}
                                size="small"
                                label="Hex Code"
                                sx={{ flexGrow: 1 }}
                            />
                        </Box>
                    </Box>
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button onClick={handleSave} variant="contained">Save</Button>
            </DialogActions>
        </Dialog>
    );
}

export default CategoriesPage;

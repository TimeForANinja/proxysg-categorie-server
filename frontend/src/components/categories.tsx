import React from 'react';
import {
    Box,
    Button,
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
    IconButton,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import DeleteIcon from "@mui/icons-material/Delete";
import SearchIcon from "@mui/icons-material/Search";
import { useNavigate } from "react-router-dom";

import {
    createCategory,
    deleteCategory,
    getCategories,
} from "../api/category";
import {ListHeader} from "./shared/ListHeader";
import {ConfirmDeletionDialog} from "./shared/ConfirmDeletionDialog";
import {TriState} from "../types/EditDialogState";
import {MyPaginator} from "./shared/MyPaginator";
import {buildLUTFromID, filterLUT, getLUTValues, LUT, pushLUT} from "../types/LookUpTable";
import {simpleNameCheck} from "../util/InputValidators";
import {BY_ID} from "../util/comparator";
import {SearchParser} from "../searchParser";
import {CategoryFieldsRaw, CategoryToKV, ICategory, IMutableCategory} from "../types/category";
import {KVaddRAW} from "../types/stringKV";
import {useBranch} from "../hooks/useBranch";

interface BuildRowProps {
    category: ICategory,
    onDelete: (cat: ICategory) => void,
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
        onDelete,
    } = props;
    const navigate = useNavigate();

    const handleSearchInUrls = () => {
        // Build a wildcard search against the URL list by categories name
        // Escape special characters that could break the quoted value
        const safeName = category.name.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
        const query = `categories="*${safeName}*"`;
        const params = new URLSearchParams({ q: query });
        navigate({ pathname: '/url', search: `?${params.toString()}` });
    };

    return (
        <TableRow key={category.id}>
            <TableCell>{category.id}</TableCell>
            <TableCell>{category.name}</TableCell>
            <TableCell>
                <IconButton aria-label="search URLs with this category" onClick={handleSearchInUrls} size="small">
                    <SearchIcon />
                </IconButton>
                <IconButton aria-label="delete category" onClick={() => onDelete(category)} size="small">
                    <DeleteIcon />
                </IconButton>
            </TableCell>
        </TableRow>
    );
});

function CategoriesPage() {
    const { currentBranch } = useBranch();
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
        [filteredRows, categories],
    );

    // Track the object (if any) for which a delete confirmation is open
    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<ICategory | null>(null);

    // load categories from the backend
    React.useEffect(() => {
        Promise.all([getCategories(currentBranch)])
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
    const handleEditDialogClose = () => {
        setEditCategory(TriState.CLOSED);
    };

    // create or edit a new object
    const handleSave = async (catID: string | null, category: IMutableCategory) => {
        if (catID == null) {
            // add the new category
            const newCat = await createCategory(currentBranch, category)
            setCategory(pushLUT(categories, newCat));
        }
        handleEditDialogClose();
    };

    const handleDelete = React.useCallback((category: ICategory) => {
        // show the dialogue to confirm the deletion
        setDeleteDialogOpen(category);
    }, []);
    const handleDeleteConfirmation = (del: boolean) => {
        // del == true means the user confirmed the popup
        if (del && isDeleteDialogOpen != null) {
            deleteCategory(currentBranch, isDeleteDialogOpen.id).then(() => {
                // remove category with ID from the store
                setCategory(filterLUT(categories, (cat => cat.id !== isDeleteDialogOpen.id)));
            });
        }
        setDeleteDialogOpen(null);
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
                    addElement={"Category"}
                    downloadRows={downloadRows}
                    availableFields={CategoryFieldsRaw}
                />
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper} style={{maxHeight: 'calc(100vh - 190px)', overflow: 'auto'}}>
                            <Table sx={{minWidth: 650}} size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell component="th" scope="row">ID</TableCell>
                                        <TableCell>Name</TableCell>
                                        <TableCell></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(cat =>
                                        <BuildRow
                                            key={cat.id}
                                            category={cat}
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
    onSave: (id: string | null, category: IMutableCategory) => void
}
function EditDialog(props: EditDialogProps) {
    let {category, onClose, onSave} = props;

    const [name, setName] = React.useState('');

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
        } else {
            setName("")
        }
    }, [category]);

    const handleSave = () => {
        if (nameError != null) {
            // only continue if the inputs are valid
            return;
        }

        onSave(category.getValue()?.id ?? null, {name});
        setName("")
    };

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleSave();
        }
    };

    return (
        <Dialog open={category.isOpen()} onClose={onClose} onKeyDown={handleKeyDown}>
            <DialogTitle>Edit Category</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                    <TextField
                        label="Name"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        error={nameError != null}
                        helperText={nameError ? nameError : ''}
                        required
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

export default CategoriesPage;

import React from 'react';
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    MenuItem,
    Paper,
    Select,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit"

import {
    createCategory,
    deleteCategory,
    getCategories,
    setSubCategory,
    updateCategory
} from "../api/category";
import {colorLUT} from "../util/colormixer";
import {useAuth} from "../model/AuthContext";
import {ListHeader} from "./shared/ListHeader";
import {ConfirmDeletionDialog} from "./shared/ConfirmDeletionDialog";
import {TriState} from "../model/types/EditDialogState";
import {MyPaginator} from "./shared/MyPaginator";
import {CategoryPicker} from "./shared/CategoryPicker";
import {buildLUTFromID, filterLUT, getLUTValues, LUT, mapLUT, pushLUT} from "../model/types/LookUpTable";
import {
    simpleNameCheck,
    simpleStringCheck,
} from "../util/InputValidators";
import {BY_ID} from "../util/comparator";
import {SearchParser} from "../searchParser";
import {CategoryFieldsRaw, CategoryToKV, ICategory, IMutableCategory} from "../model/types/category";
import {KVaddRAW} from "../model/types/stringKV";

interface BuildRowProps {
    category: ICategory,
    updateCategory: (newCategory: ICategory) => void,
    categories: LUT<ICategory>,
    onEdit: (cat: ICategory) => void,
    onDelete: (cat: ICategory) => void,
}
/**
 * Renders a table row for a Category entry.
 *
 * Wrapped in React.memo to prevent unnecessary re-renders in the Category table.
 * This works as long as none of the props passed to the Component change
 *
 * The caching also requires us to ensure that all callbacks passed are constants (e.g. wrapped in useCallable)
 */
const BuildRow = React.memo(function BuildRow(props: BuildRowProps) {
    const {
        category,
        updateCategory,
        categories,
        onEdit,
        onDelete
    } = props;
    const authMgmt = useAuth();

    // helper function, triggered when the category selector changes
    const handleChange = (newList: string[]) => {
        // update api
        setSubCategory(authMgmt.token, category.id, newList).then(newCats => {
            // save the new version
            const newCat = {...category, nested_categories: newCats};
            updateCategory(newCat);
        })
    };

    return (
        <TableRow key={category.id}>
            <TableCell>{category.id}</TableCell>
            <TableCell>{category.name}</TableCell>
            <TableCell>
                <div style={{
                    backgroundColor: colorLUT[category.color].bg,
                    color: colorLUT[category.color].fg,
                    width: '20px',
                    height: '20px',
                }}/>
            </TableCell>
            <TableCell>{category.description}</TableCell>
            <TableCell>
                <CategoryPicker
                    isCategories={category.nested_categories}
                    onChange={(newList) => handleChange(newList)}
                    categories={categories}
                />
            </TableCell>
            <TableCell>
                <EditIcon onClick={() => onEdit(category)}/>
                <DeleteIcon onClick={() => onDelete(category)}/>
            </TableCell>
        </TableRow>
    );
});

function CategoriesPage() {
    const authMgmt = useAuth();

    // State info for the Page
    const [categories, setCategory] = React.useState<LUT<ICategory>>({});

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<ICategory[]>([]);
    const comparator = BY_ID;
    const [quickSearch, setQuickSearch] = React.useState<SearchParser | null>(null);
    // Memoize the filtered rows to avoid unnecessary recalculations
    const filteredRows = React.useMemo(
        () => getLUTValues(categories).filter(x => {
            return quickSearch?.test(KVaddRAW(CategoryToKV(x, categories))) ?? true;
        }),
        [quickSearch, categories],
    );

    // Memoize the download rows to avoid unnecessary transformations
    const downloadRows = React.useMemo(
        () => filteredRows.map(row => CategoryToKV(row, categories)),
        [filteredRows, categories],
    );

    // Track the object (if any) for which a delete confirmation is open
    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<ICategory | null>(null);

    // load categories from the backend
    React.useEffect(() => {
        Promise.all([getCategories(authMgmt.token)])
            .then(([categoriesData]) => {
                setCategory(buildLUTFromID(categoriesData));
            })
            .catch((error) => console.error("Error:", error));
    }, [authMgmt]);

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
            const newCat = await createCategory(authMgmt.token, category)
            setCategory(pushLUT(categories, newCat));
        } else {
            const newCat = await updateCategory(authMgmt.token, catID, category)
            // "replace" existing category if id matches
            setCategory(mapLUT(categories, (cat => cat.id === catID ? newCat : cat)));
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
            deleteCategory(authMgmt.token, isDeleteDialogOpen.id).then(() => {
                // remove category with ID from the store
                setCategory(filterLUT(categories, (cat => cat.id !== isDeleteDialogOpen.id)));
            });
        }
        setDeleteDialogOpen(null);
    }

    // save an updated URL object in the urls cache
    const handleUpdateCategory = React.useCallback(
        (newCat: ICategory) => setCategory(mapLUT(categories, (cat => cat.id === newCat.id ? newCat : cat))),
        [categories]
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
                                        <TableCell>Color</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell>Sub-Categories</TableCell>
                                        <TableCell></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(cat =>
                                        <BuildRow
                                            key={cat.id}
                                            categories={categories}
                                            updateCategory={handleUpdateCategory}
                                            category={cat}
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
    const [description, setDescription] = React.useState('');
    const [color, setColor] = React.useState(1);

    // validate inputs
    const nameError: string|null = React.useMemo(
        () => simpleNameCheck(name, true),
        [name],
    )
    const descriptionError: string|null = React.useMemo(
        () => simpleStringCheck(description),
        [description],
    )

    React.useEffect(() => {
        // set existing values if a category was provided
        // else force clear the fields
        if (!category.isNull()) {
            setName(category.getValue()!.name);
            setDescription(category.getValue()!.description);
            setColor(category.getValue()!.color);
        } else {
            setName("")
            setDescription("")
            setColor(1)
        }
    }, [category]);

    const handleSave = () => {
        if (nameError != null || descriptionError != null) {
            // only continue if the inputs are valid
            return;
        }

        onSave(category.getValue()?.id ?? null, {name, description, color});
        setName("")
        setDescription("")
        setColor(1)
    };

    return (
        <Dialog open={category.isOpen()} onClose={onClose}>
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
                    <TextField
                        label="Description"
                        value={description}
                        onChange={e => setDescription(e.target.value)}
                        error={descriptionError != null}
                        helperText={descriptionError ? descriptionError : ''}
                    />
                    <Select
                        value={color.toString()}
                        label="Color"
                        onChange={(e) => setColor(Number(e.target.value))}
                    >
                        {
                            Object.keys(colorLUT).map(c => Number(c)).map((key) => (
                                <MenuItem key={key} value={key.toString()}>
                                    <div style={{
                                        backgroundColor: colorLUT[key].bg,
                                        color: colorLUT[key].fg,
                                        width: '20px',
                                        height: '20px'
                                    }}/>
                                </MenuItem>
                            ))
                        }
                    </Select>
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

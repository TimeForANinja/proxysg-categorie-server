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
    ICategory,
    IMutableCategory, setSubCategory,
    updateCategory
} from "../api/categories";
import {colors} from "../util/colormixer";
import {useAuth} from "../model/AuthContext";
import {ListHeader} from "./shared/list-header";
import {ConfirmDeletionDialog} from "./shared/ConfirmDeletionDialog";
import {TriState} from "../model/types/EditDialogState";
import {MyPaginator} from "./shared/paginator";
import {CategoryPicker} from "./shared/CategoryPicker02";
import {buildLUTFromID, filterLUT, getLUTValues, LUT, mapLUT, pushLUT} from "../model/types/LookUpTable";
import {
    simpleNameCheck,
    simpleStringCheck,
} from "../util/InputValidators";
import {BY_ID} from "../util/comparator";

interface BuildRowProps {
    category: ICategory,
    updateCategory: (newCategory: ICategory) => void,
    categories: LUT<ICategory>,
    onEdit: () => void,
    onDelete: () => void,
}
function BuildRow(props: BuildRowProps) {
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
                <div style={{backgroundColor: colors[category.color], width: '20px', height: '20px'}}/>
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
                <EditIcon onClick={onEdit}/>
                <DeleteIcon onClick={onDelete}/>
            </TableCell>
        </TableRow>
    );
}

function CategoriesPage() {
    const authMgmt = useAuth();

    // State info for the Page
    const [categories, setCategory] = React.useState<LUT<ICategory>>({});

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<ICategory[]>([]);
    const comparator = BY_ID;
    const [quickSearch, setQuickSearch] = React.useState('');
    const filteredRows = React.useMemo(
        () =>
            getLUTValues(categories).filter(x => {
                // TODO: not sure if switching to sth. like "levenshtein distance" makes more sense?
                const cat_str = x.nested_categories.map(c => categories[c]?.name).join(' ');
                const search_str = `${x.id} ${x.name} ${x.description} ${cat_str}`;
                return search_str.toLowerCase().includes(quickSearch.toLowerCase());
            }),
        [quickSearch, categories],
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
    const handleEditOpen = (category: ICategory | null = null) => {
        setEditCategory(category ? new TriState(category) : TriState.NEW);
    };
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

    const handleDelete = (category: ICategory) => {
        // show the dialogue to confirm the deletion
        setDeleteDialogOpen(category);
    }
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
                    downloadRows={null}
                />
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper}>
                            <Table sx={{minWidth: 650}} size="small">
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
                                            updateCategory={newCat => setCategory(mapLUT(categories, (cat => cat.id === newCat.id ? newCat : cat)))}
                                            category={cat}
                                            onEdit={() => handleEditOpen(cat)}
                                            onDelete={() => handleDelete(cat)}
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
                            Object.keys(colors).map(c => Number(c)).map((key) => (
                                <MenuItem key={key} value={key.toString()}>
                                    <div style={{backgroundColor: colors[key], width: '20px', height: '20px'}}/>
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

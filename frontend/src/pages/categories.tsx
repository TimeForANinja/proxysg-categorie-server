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
import {TriState} from "./shared/EditDialogState";
import {MyPaginator} from "./shared/paginator";
import {CategoryPicker} from "./shared/CategoryPicker02";
import {buildLUTFromID, filterLUT, getLUTValues, LUT, mapLUT, pushLUT} from "../util/LookUpTable";

const COMPARATORS = {
    BY_ID:  (a: ICategory, b: ICategory) => a.id - b.id
};

interface BuildRowProps {
    category: ICategory,
    categories: LUT<ICategory>,
    onEdit: () => void,
    onDelete: () => void,
}
function BuildRow(props: BuildRowProps) {
    const {
        category,
        categories,
        onEdit,
        onDelete
    } = props;
    const authMgmt = useAuth();

    const [isCategories, setCategories] = React.useState(category.nested_categories);

    // helper function, triggered when category selector changes
    const handleChange = (newList: number[]) => {
        // update api
        setSubCategory(authMgmt.token, category.id, newList).then(newCats => {
            // save new version
            setCategories(newCats);
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
                    isCategories={isCategories}
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
    const [categories, setCategory] = React.useState<LUT<ICategory>>([]);

    // search & pagination
    const [visibleRows, setVisibleRows] = React.useState<ICategory[]>([]);
    const comparator = COMPARATORS.BY_ID;
    const [quickSearch, setQuickSearch] = React.useState('');
    const filteredRows = React.useMemo(
        () =>
            getLUTValues(categories).filter(x => {
                // not sure if switching to sth. like "levenshtein distance" makes more sense?
                return `${x.id} ${x.name} ${x.description}`.toLowerCase().includes(quickSearch.toLowerCase())
            }),
        [quickSearch, categories],
    );

    // Track object (if any) for which a delete confirmation is open
    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<ICategory | null>(null);

    // load categories from backend
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

    // create or edit new object
    const handleSave = (catID: number|null, category: IMutableCategory) => {
        if (catID == null) {
            // add new category
            createCategory(authMgmt.token, category).then(newCat => {
                setCategory(pushLUT(categories, newCat));
            });
        } else {
            updateCategory(authMgmt.token, catID, category).then(newCat => {
                // "replace" existing category if id matches
                setCategory(mapLUT(categories, (cat => cat.id === catID ? newCat : cat)));
            })
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
                // remove category with ID from store
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
                />
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 650 }} size="small">
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
    onSave: (id: number | null, category: IMutableCategory) => void
}
function EditDialog(props: EditDialogProps) {
    let {category, onClose, onSave} = props;

    const [name, setName] = React.useState('');
    const [description, setDescription] = React.useState('');
    const [color, setColor] = React.useState(1);

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
                        onChange={(e) => setName(e.target.value)}
                    />
                    <TextField
                        label="Description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
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

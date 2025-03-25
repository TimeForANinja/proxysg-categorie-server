import React from 'react';
import {
    getCategories,
    ICategory,
    deleteCategory,
    createCategory,
    updateCategory,
    IMutableCategory
} from "../api/categories";
import {colors} from "../util/colormixer";
import Paper from "@mui/material/Paper";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit"
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import {DialogContentText} from "@mui/material";

function BuildRow(props: {
    category: ICategory,
    onEdit: () => void,
    onDelete: () => void,
}) {
    const {
        category,
        onEdit,
        onDelete,
    } = props;

    return (
        <TableRow key={category.id}>
            <TableCell>{category.id}</TableCell>
            <TableCell>{category.name}</TableCell>
            <TableCell>
                <div style={{backgroundColor: colors[category.color], width: '20px', height: '20px'}}/>
            </TableCell>
            <TableCell>{category.description}</TableCell>
            <TableCell>
                <EditIcon onClick={onEdit}/>
                <DeleteIcon onClick={onDelete}/>
            </TableCell>
        </TableRow>
    );
}

function CategoriesPage() {
    const [categories, setCategory] = React.useState<ICategory[]>([]);
    const [editCategory, setEditCategory] = React.useState<ICategory | null>(null);
    const [isEditDialogOpen, setEditDialogOpen] = React.useState(false);
    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<ICategory | null>(null);

    // load categories from backend
    React.useEffect(() => {
        Promise.all([getCategories()])
            .then(([categoriesData]) => {
                setCategory(categoriesData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    const handleEditOpen = (category: ICategory | null) => {
        setEditCategory(category);
        setEditDialogOpen(true);
    };

    const handleEditDialogClose = () => {
        setEditDialogOpen(false);
    };

    const handleSave = (catID: number|null, category: IMutableCategory) => {
        if (catID == null) {
            // add new category
            createCategory(category).then(newCat => {
                setCategory([...categories, newCat]);
            });
        } else {
            updateCategory(catID, category).then(newCat => {
                // "replace" existing category if id matches
                setCategory(categories.map(cat => cat.id === catID ? newCat : cat));
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
            deleteCategory(isDeleteDialogOpen.id).then(() => {
                // remove category with ID from store
                setCategory(categories.filter(cat => cat.id !== isDeleteDialogOpen.id));
            });
        }
        setDeleteDialogOpen(null);
    }

    return (
        <>
            <React.Fragment>
                <Dialog
                    open={isDeleteDialogOpen != null}
                    onClose={() => handleDeleteConfirmation(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle id="alert-dialog-title">
                        {"Delete Category?"}
                    </DialogTitle>
                    <DialogContent>
                        <DialogContentText id="alert-dialog-description">
                            Are you sure you want to Delete the Category?
                            This will also unassign the Category from all URLs.
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => handleDeleteConfirmation(false)}>Disagree</Button>
                        <Button onClick={() => handleDeleteConfirmation(true)} autoFocus>
                            Agree
                        </Button>
                    </DialogActions>
                </Dialog>
            </React.Fragment>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell component="th" scope="row">ID</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Color</TableCell>
                            <TableCell>Description</TableCell>
                            <TableCell></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {categories.map(cat =>
                            <BuildRow
                                key={cat.id}
                                category={cat}
                                onEdit={() => handleEditOpen(cat)}
                                onDelete={() => handleDelete(cat)}
                            />
                        )}
                        <TableRow>
                            <TableCell colSpan={5} align="center">
                                <Button onClick={() => handleEditOpen(null)}>
                                    + Add Category
                                </Button>
                            </TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableContainer>
            <EditDialog
                isOpen={isEditDialogOpen}
                category={editCategory}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

function EditDialog(props: {
    isOpen: boolean,
    category: ICategory | null,
    onClose: () => void,
    onSave: (id: number | null, category: IMutableCategory) => void
}) {
    let {isOpen, category, onClose, onSave} = props;

    const [name, setName] = React.useState('');
    const [description, setDescription] = React.useState('');
    const [color, setColor] = React.useState(1);

    React.useEffect(() => {
        if (category) {
            setName(category.name);
            setDescription(category.description);
            setColor(category.color);
        } else {
            setName("")
            setDescription("")
            setColor(1)
        }
    }, [category]);

    const handleSave = () => {
        onSave(category?.id ?? null, {name, description, color});
        setName("")
        setDescription("")
        setColor(1)
    };

    return (
        <Dialog open={isOpen} onClose={onClose}>
            <DialogTitle>Edit Category</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                    <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)}/>
                    <TextField label="Description" value={description}
                               onChange={(e) => setDescription(e.target.value)}/>
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

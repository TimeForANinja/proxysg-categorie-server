import React from 'react';
import {getCategories, ICategory} from "../api/categories";
import {colors} from "../api/colormixer";
import Paper from "@mui/material/Paper";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit"
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";

const ModalStyle = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
};


function BuildRow(props: {
    category: ICategory,
    onEdit: (category: ICategory) => void,
}) {
    const { category } = props;
    const handleEdit = (category: ICategory) => {
        props.onEdit(category);
    };

    return (
        <TableRow key={category.id}>
            <TableCell>{category.id}</TableCell>
            <TableCell>{category.name}</TableCell>
            <TableCell>
                <div style={{ backgroundColor: colors[category.color], width: '20px', height: '20px' }} />
            </TableCell>
            <TableCell>{category.description}</TableCell>
            <TableCell>
                <EditIcon onClick={() => handleEdit(category)} />
                <DeleteIcon />
            </TableCell>
        </TableRow>
    );
}

function CategoriesPage() {
    const [categories, setCategory] = React.useState<ICategory[]>([]);
    const [selectedCategory, setSelectedCategory] = React.useState<ICategory | null>(null);
    const [isDialogOpen, setDialogOpen] = React.useState(false);

    React.useEffect(() => {
        Promise.all([getCategories()])
            .then(([categoriesData]) => {
                setCategory(categoriesData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);
    const handleEditOpen = (category: ICategory) => {
        setSelectedCategory(category);
        setDialogOpen(true);
    };

    const handleDialogClose = () => {
        setDialogOpen(false);
    };

    const handleSave = (category: ICategory) => {
        if (category.id === -1) {
            // add new category
            category.id = Math.max(...categories.map(cat => cat.id)) + 1;
            setCategory([...categories, category]);
        } else {
            // "replace" existing category if id matches
            setCategory(categories.map(cat => cat.id === category.id ? category : cat));
        }
        setDialogOpen(false);
    };

    return (
        <>
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
                    {categories.map(cat => <BuildRow category={cat} onEdit={handleEditOpen} />)}
                    <TableRow>
                        <TableCell colSpan={5} align="center">
                            <Button onClick={() => handleEditOpen({ id: -1, name: '', description: '', color: 0 })}>
                                + Add Category
                            </Button>
                        </TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        </TableContainer>
        {selectedCategory && (
            <EditDialog
                isOpen={isDialogOpen}
                category={selectedCategory}
                onClose={handleDialogClose}
                onSave={handleSave}
            />
        )}
        </>
    );
}

function EditDialog(props: {
    isOpen: boolean,
    category: ICategory,
    onClose: () => void,
    onSave: (category: ICategory) => void
}) {
    const { isOpen, category, onClose, onSave } = props;
    const [name, setName] = React.useState(category.name);
    const [description, setDescription] = React.useState(category.description);
    const [color, setColor] = React.useState(category.color);

    React.useEffect(() => {
        if (category) {
            setName(category.name);
            setDescription(category.description);
            setColor(category.color);
        }
    }, [category]);

    const handleSave = () => {
        // TODO: when changing color it's for some reason shifted by one
        onSave({ ...category, name, description, color });
    };

    return (
        <Dialog open={isOpen} onClose={onClose}>
            <DialogTitle>Edit Category</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                    <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)} />
                    <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
                    <Select
                        value={color.toString()}
                        label="Color"
                        onChange={(e) => setColor(Number(e.target.value))}
                    >
                        {
                            Array.from(Object.values(colors)).map((color, colorIDX) => (
                                <MenuItem key={colorIDX} value={colorIDX}>
                                    <div style={{ backgroundColor: color, width: '20px', height: '20px' }} />
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

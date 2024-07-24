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

function CategoriesPage() {
    const [categories, setCategory] = React.useState<ICategory[]>([]);

    React.useEffect(() => {
        Promise.all([getCategories()])
            .then(([categoriesData]) => {
                setCategory(categoriesData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                <TableRow>
                    <TableCell component="th" scope="row">ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Color</TableCell>
                </TableRow>
                </TableHead>
                <TableBody>
                {categories.map(category => (
                    <TableRow key={category.id}>
                        <TableCell>{category.id}</TableCell>
                        <TableCell>{category.name}</TableCell>
                        <TableCell style={{
                            backgroundColor: colors[category.color],
                        }}>{colors[category.color]}</TableCell>
                    </TableRow>
                ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default CategoriesPage;

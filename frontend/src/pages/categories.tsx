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

function BuildRow(props: { category: ICategory }) {
    const { category } = props;
    const [isColor, setColor] = React.useState(category.color);

    const handleChange = (event: SelectChangeEvent) => {
        setColor(Number(event.target.value));
        // setAge(event.target.value as string);
    };

    return (
        <TableRow key={category.id}>
            <TableCell>{category.id}</TableCell>
            <TableCell>{category.name}</TableCell>
            <TableCell>
                <Select
                    value={isColor.toString()}
                    label="Color"
                    onChange={handleChange}
                >
                    {
                        Array.from(Object.values(colors)).map((color, colorIDX) => {
                            return (
                                <MenuItem value={colorIDX}>
                                    <div style={{backgroundColor: color}}>{color}</div>
                                </MenuItem>
                            )
                        })
                    }
                </Select>
            </TableCell>
            <TableCell>{category.description}</TableCell>
            <TableCell><DeleteIcon/></TableCell>
        </TableRow>
    )
}

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
                    <TableCell>Description</TableCell>
                    <TableCell></TableCell>
                </TableRow>
                </TableHead>
                <TableBody>
                {categories.map(cat => <BuildRow category={cat}/>)}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default CategoriesPage;

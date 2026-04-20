import React from 'react';
import {
    IconButton,
    TableCell,
    TableRow,
} from "@mui/material";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from "react-router-dom";

import { getHistory } from "../../api/history";
import {ICategory, IRestCategoryDetail} from "../../types/category";
import { IRestCommit } from "../../types/history";
import { useAuth } from "../../hooks/useLogin";
import HistoryTable from "../shared/HistoryTable";
import { Collapse, Box } from "@mui/material";
import {short_uuid} from "../../util/uuid";
import {colorToHex} from "../../util/colormixer";
import {CategoryPicker} from "../shared/CategoryPicker";
import {addCategoryChild, deleteCategoryChild} from "../../api/mapping";
import {LUT, mapLUT} from "../../types/LookUpTable";

export interface CategoryRowProps {
    category: IRestCategoryDetail,
    categories: LUT<IRestCategoryDetail>,
    onEdit: (cat: ICategory) => void,
    onDelete: (cat: ICategory) => void,
    onRefresh: () => void,
    isLocked: boolean,
    branch: string,
}

export const CategoryRow = React.memo(function CategoryRow(props: CategoryRowProps) {
    const {
        category,
        categories,
        onEdit,
        onDelete,
        onRefresh,
        isLocked,
        branch,
    } = props;
    const authMgmt = useAuth();
    const navigate = useNavigate();

    const [open, setOpen] = React.useState(false);
    const [history, setHistory] = React.useState<IRestCommit[]>([]);

    const handleSearchInUrls = () => {
        const safeName = category.category.name.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
        const query = `categories="*${safeName}*"`;
        const params = new URLSearchParams({ q: query });
        navigate({ pathname: '/url', search: `?${params.toString()}` });
    };

    const toggleOpen = () => {
        if (!open && history.length === 0) {
            getHistory(authMgmt.token, branch, [category.category.id])
                .then(setHistory)
                .catch(err => console.error('Failed to load history:', err));
        }
        setOpen(prev => !prev);
    };

    const handleAddCategory = async (childCat: ICategory) => {
        await addCategoryChild(authMgmt.token, category.category.id, childCat.id);
        onRefresh();
    };

    const handleDeleteCategory = async (childCat: ICategory) => {
        await deleteCategoryChild(authMgmt.token, category.category.id, childCat.id);
        onRefresh();
    };

    return (
        <React.Fragment>
            <TableRow key={category.category.id} sx={{ '& > *': { borderBottom: 'unset' } }}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={toggleOpen}
                    >
                        {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{short_uuid(category.category.id)}</TableCell>
                <TableCell>{category.category.name}</TableCell>
                <TableCell>{category.category.description}</TableCell>
                <TableCell>
                    <Box sx={{
                        width: 24,
                        height: 24,
                        border: '1px solid grey',
                        borderRadius: '8px',
                        alignItems: 'center',
                        display: 'flex',
                        justifyContent: 'center',
                        bgcolor: colorToHex(category.category.color),
                    }}/>
                </TableCell>
                <TableCell>
                    <CategoryPicker
                        categories={mapLUT(categories, c => c.category)}
                        isCategories={category.children}
                        onChange={(newIds, added, removed) => {
                            added.forEach(id => handleAddCategory(categories[id].category));
                            removed.forEach(id => handleDeleteCategory(categories[id].category));
                        }}
                        disabled={isLocked}
                    />
                </TableCell>
                <TableCell align="right">
                    <IconButton aria-label="search in urls" onClick={handleSearchInUrls} size="small">
                        <SearchIcon fontSize="small" />
                    </IconButton>
                    {!isLocked && (
                        <>
                            <IconButton aria-label="edit category" onClick={() => onEdit(category.category)} size="small">
                                <EditIcon />
                            </IconButton>
                            <IconButton aria-label="delete category" onClick={() => onDelete(category.category)} size="small">
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
                            <HistoryTable commits={history} small />
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    );
});

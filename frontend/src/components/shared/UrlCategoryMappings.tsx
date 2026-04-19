import React from 'react';
import {
    Autocomplete,
    Box,
    IconButton,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import { addURLCategory, deleteURLCategory } from "../../api/url";
import { useAuth } from "../../hooks/useLogin";
import { IRestURLDetail } from "../../types/url";
import { ICategory } from "../../types/category";
import { LUT, getLUTValues } from "../../types/LookUpTable";
import { formatConstraint } from "../../util/DateString";

interface UrlCategoryMappingsProps {
    urlDetail: IRestURLDetail;
    isLocked: boolean;
    categories: LUT<ICategory>;
    onRefresh: () => void;
}

export const UrlCategoryMappings: React.FC<UrlCategoryMappingsProps> = ({
    urlDetail,
    isLocked,
    categories,
    onRefresh,
}) => {
    const authMgmt = useAuth();
    const [categorySearch, setCategorySearch] = React.useState('');

    // State for the "Add Mapping" row
    const [newCategoryId, setNewCategoryId] = React.useState<string | null>(null);
    const [newStartDate, setNewStartDate] = React.useState<string>('');
    const [newEndDate, setNewEndDate] = React.useState<string>('');

    const filteredMappings = urlDetail.categories.filter(m =>
        m.category.name.toLowerCase().includes(categorySearch.toLowerCase())
    );

    const availableCategories = React.useMemo(() => {
        const usedCategoryIds = new Set(urlDetail.categories.map(m => m.category.id));
        return getLUTValues(categories).filter(c => !usedCategoryIds.has(c.id));
    }, [categories, urlDetail.categories]);

    const handleAddMapping = async () => {
        if (!newCategoryId) return;

        const start = newStartDate ? Math.floor(new Date(newStartDate).getTime() / 1000) : 0;
        const end = newEndDate ? Math.floor(new Date(newEndDate).getTime() / 1000) : 0;

        try {
            await addURLCategory(authMgmt.token, newCategoryId, {
                url: urlDetail.url.id,
                constraint: (start || end) ? { comment: '', start, end } : undefined
            });
            setNewCategoryId(null);
            setNewStartDate('');
            setNewEndDate('');
            onRefresh();
        } catch (e) {
            console.error(e);
        }
    };

    const handleDeleteMapping = async (categoryId: string) => {
        try {
            await deleteURLCategory(authMgmt.token, categoryId, urlDetail.url.id);
            onRefresh();
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <Box sx={{ margin: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="h6" gutterBottom component="div">
                    URL Category Mappings
                </Typography>
            </Box>
            <TextField
                size="small"
                placeholder="Search mappings..."
                value={categorySearch}
                onChange={(e) => setCategorySearch(e.target.value)}
                sx={{ mb: 1, width: '100%' }}
            />
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 300 }}>
                <Table size="small" stickyHeader>
                    <TableHead>
                        <TableRow>
                            <TableCell>Category</TableCell>
                            <TableCell>Constraint</TableCell>
                            <TableCell align="right" style={{ width: 50 }}>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {!isLocked && (
                            <TableRow sx={{ backgroundColor: 'action.hover' }}>
                                <TableCell>
                                    <Autocomplete
                                        size="small"
                                        options={availableCategories}
                                        getOptionLabel={(option) => option.name}
                                        renderInput={(params) => <TextField {...params} label="Select Category" />}
                                        value={newCategoryId ? categories[newCategoryId] : null}
                                        onChange={(_, newValue) => setNewCategoryId(newValue?.id ?? null)}
                                    />
                                </TableCell>
                                <TableCell>
                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                        <TextField
                                            type="date"
                                            size="small"
                                            value={newStartDate}
                                            onChange={(e) => setNewStartDate(e.target.value)}
                                        />
                                        <Typography sx={{ alignSelf: 'center' }}>-</Typography>
                                        <TextField
                                            type="date"
                                            size="small"
                                            value={newEndDate}
                                            onChange={(e) => setNewEndDate(e.target.value)}
                                        />
                                    </Box>
                                </TableCell>
                                <TableCell align="right">
                                    <IconButton
                                        size="small"
                                        color="primary"
                                        onClick={handleAddMapping}
                                        disabled={!newCategoryId}
                                    >
                                        <AddIcon />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        )}
                        {filteredMappings.map((m) => {
                            return (
                                <TableRow key={m.category.id}>
                                    <TableCell>{m.category.name}</TableCell>
                                    <TableCell>
                                        {m.constraint ? (
                                            <span>{formatConstraint(m.constraint)}</span>
                                        ) : '-'}
                                    </TableCell>
                                    <TableCell align="right">
                                        {!isLocked && (
                                            <IconButton
                                                size="small"
                                                onClick={() => handleDeleteMapping(m.category.id)}
                                                color="error"
                                            >
                                                <DeleteIcon fontSize="inherit" />
                                            </IconButton>
                                        )}
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

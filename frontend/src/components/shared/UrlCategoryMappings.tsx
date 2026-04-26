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
    Collapse,
    Grid,
    Button, Tooltip,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import { addURLCategory, deleteURLCategory } from "../../api/mapping";
import { useAuth } from "../../hooks/useLogin";
import { useNotification } from "../../hooks/useNotification";
import { IRestURLDetail } from "../../types/url";
import { ICategory } from "../../types/category";
import { CategoryChip } from "./CategoryChip";
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
    const { showError, showSuccess } = useNotification();
    const [categorySearch, setCategorySearch] = React.useState('');

    // State for the "Add Mapping" row
    const [newCategoryId, setNewCategoryId] = React.useState<string | null>(null);
    const [newStartDate, setNewStartDate] = React.useState<string>('');
    const [newEndDate, setNewEndDate] = React.useState<string>('');
    const [newComment, setNewComment] = React.useState<string>('');

    const [isAddExpanded, setIsAddExpanded] = React.useState(false);

    const filteredMappings = React.useMemo(() => {
        return urlDetail.categories.filter(m =>
            m.category.name.toLowerCase().includes(categorySearch.toLowerCase())
        );
    }, [urlDetail.categories, categorySearch]);

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
                url_id: urlDetail.url.id,
                constraint: (start || end || newComment) ? { comment: newComment, start, end } : undefined
            });
            showSuccess("Mapping added successfully");
            setNewCategoryId(null);
            setNewStartDate('');
            setNewEndDate('');
            setNewComment('');
            setIsAddExpanded(false);
            onRefresh();
        } catch (e: any) {
            showError(e.message);
        }
    };

    const handleDeleteMapping = async (categoryId: string) => {
        try {
            await deleteURLCategory(authMgmt.token, categoryId, urlDetail.url.id);
            showSuccess("Mapping removed successfully");
            onRefresh();
        } catch (e: any) {
            showError(e.message);
        }
    };

    return (
        <Box sx={{ p: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
                    URL Mappings
                </Typography>
                {!isLocked && (
                    <Button
                        variant="contained"
                        size="small"
                        startIcon={isAddExpanded ? <DeleteIcon /> : <AddIcon />}
                        onClick={() => setIsAddExpanded(!isAddExpanded)}
                        color={isAddExpanded ? "inherit" : "primary"}
                    >
                        {isAddExpanded ? "Cancel" : "Add Mapping"}
                    </Button>
                )}
            </Box>

            <Collapse in={isAddExpanded}>
                <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'primary.50', borderColor: 'primary.light' }}>
                    <Grid container spacing={2}>
                        <Grid size={{ xs: 12, md: 5 }}>
                            <Autocomplete
                                size="small"
                                options={availableCategories}
                                getOptionLabel={(option) => option.name}
                                renderInput={(params) => <TextField {...params} label="Category" required />}
                                value={newCategoryId ? categories[newCategoryId] : null}
                                onChange={(_, newValue) => setNewCategoryId(newValue?.id ?? null)}
                                renderOption={(props, option) => {
                                    const { key, ...optionProps } = props;
                                    const colorHex = `#${option.color.toString(16).padStart(6, '0')}`;
                                    return (
                                        <li key={key} {...optionProps}>
                                            <Box
                                                sx={{
                                                    width: 16,
                                                    height: 16,
                                                    borderRadius: '50%',
                                                    bgcolor: colorHex,
                                                    mr: 1,
                                                    border: '1px solid grey'
                                                }}
                                            />
                                            {option.name}
                                        </li>
                                    );
                                }}
                                fullWidth
                            />
                        </Grid>
                        <Grid size={{ xs: 12, md: 3 }}>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                                <TextField
                                    type="date"
                                    size="small"
                                    label="Start"
                                    slotProps={{ inputLabel: { shrink: true } }}
                                    value={newStartDate}
                                    onChange={(e) => setNewStartDate(e.target.value)}
                                    fullWidth
                                />
                                <TextField
                                    type="date"
                                    size="small"
                                    label="End"
                                    slotProps={{ inputLabel: { shrink: true } }}
                                    value={newEndDate}
                                    onChange={(e) => setNewEndDate(e.target.value)}
                                    fullWidth
                                />
                            </Box>
                        </Grid>
                        <Grid size={{ xs: 12, md: 3 }}>
                            <TextField
                                size="small"
                                label="Comment"
                                value={newComment}
                                onChange={(e) => setNewComment(e.target.value)}
                                fullWidth
                            />
                        </Grid>
                        <Grid size={{ xs: 12, md: 1 }} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                            <IconButton
                                color="primary"
                                onClick={handleAddMapping}
                                disabled={!newCategoryId}
                                sx={{ bgcolor: 'white', '&:hover': { bgcolor: 'primary.100' }, width: 40, height: 40 }}
                            >
                                <AddIcon />
                            </IconButton>
                        </Grid>
                    </Grid>
                </Paper>
            </Collapse>

            <TextField
                size="small"
                placeholder="Filter mappings by category name..."
                value={categorySearch}
                onChange={(e) => setCategorySearch(e.target.value)}
                sx={{ mb: 1, width: '100%' }}
            />
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 350 }}>
                <Table sx={{ '& .MuiTableCell-root': { fontFamily: 'monospace' } }} size="small" stickyHeader>
                    <TableHead>
                        <TableRow>
                            <TableCell sx={{ fontWeight: 'bold' }}>Category</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Time Range</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Comment</TableCell>
                            <TableCell align="right" style={{ width: 50 }} sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {filteredMappings.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} align="center" sx={{ py: 3, color: 'text.secondary' }}>
                                    No mappings found.
                                </TableCell>
                            </TableRow>
                        ) : (
                            filteredMappings.map((m) => {
                                const timeRange = m.constraint && (m.constraint.start || m.constraint.end) ? (
                                    `${m.constraint.start ? new Date(m.constraint.start * 1000).toISOString().split('T')[0] : '...'} - ${m.constraint.end ? new Date(m.constraint.end * 1000).toISOString().split('T')[0] : '...'}`
                                ) : '-';
                                return (
                                    <TableRow key={m.category.id} hover>
                                        <TableCell>
                                            <CategoryChip category={m.category} variant="outlined" />
                                        </TableCell>
                                        <TableCell sx={{ fontSize: '0.85rem' }}>
                                            {timeRange}
                                        </TableCell>
                                        <TableCell sx={{ fontSize: '0.85rem', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            <Tooltip title={m.constraint?.comment || ''}>
                                                <span>{m.constraint?.comment || '-'}</span>
                                            </Tooltip>
                                        </TableCell>
                                        <TableCell align="right">
                                            {!isLocked && (
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleDeleteMapping(m.category.id)}
                                                    color="error"
                                                >
                                                    <DeleteIcon fontSize="small" />
                                                </IconButton>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                );
                            })
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

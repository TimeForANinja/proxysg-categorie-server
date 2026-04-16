import React from 'react';
import {
    Autocomplete,
    Box,
    Button,
    Chip,
    Collapse,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    IconButton,
    Paper,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
    Tooltip,
} from "@mui/material";
import Grid from '@mui/material/Grid';
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

import {addURLCategory, createURL, deleteURL, deleteURLCategory, getURLs, updateURL} from "../api/url"
import {ListHeader} from "./shared/ListHeader";
import {MyPaginator} from "./shared/MyPaginator";
import {SearchParser} from "../searchParser";
import {getHistory} from "../api/history";
import {KVaddRAW} from "../types/stringKV";
import { useBranch } from "../hooks/useBranch";
import {IConstraint, IRestURLDetail, UrlMappingFieldsRaw, URLMappingToKV} from "../types/url";
import HistoryTable from "./shared/HistoryTable";
import {IRestCommit} from "../types/history";
import {TriState} from "../types/EditDialogState";
import {ConfirmDeletionDialog} from "./shared/ConfirmDeletionDialog";
import {CategoryPicker} from "./shared/CategoryPicker";
import {getCategories} from "../api/category";
import {buildLUTFromID, getLUTValues, LUT} from "../types/LookUpTable";
import {ICategory} from "../types/category";
import {formatConstraint} from "../util/DateString";
import {simpleStringCheck} from "../util/InputValidators";

interface BuildRowProps {
    urlDetail: IRestURLDetail,
    branch: string,
    onEdit: (url: IRestURLDetail) => void,
    onDelete: (url: IRestURLDetail) => void,
    categories: LUT<ICategory>,
    onRefresh: () => void,
}
/**
 * Renders a table row for a URL entry.
 *
 * Wrapped in React.memo to prevent unnecessary re-renders in the URL table.
 * This works as long as none of the props passed to the Component change
 *
 * The caching also requires us to ensure that all callbacks passed are constants (e.g., wrapped in useCallable)
 */
const BuildRow = React.memo(function BuildRow(props: BuildRowProps) {
    const { urlDetail, branch, onEdit, onDelete, categories, onRefresh } = props;
    const [open, setOpen] = React.useState(false);
    const [history, setHistory] = React.useState<IRestCommit[]>([]);
    const [categorySearch, setCategorySearch] = React.useState('');

    // State for the "Add Mapping" row
    const [newCategoryId, setNewCategoryId] = React.useState<string | null>(null);
    const [newStartDate, setNewStartDate] = React.useState<string>('');
    const [newEndDate, setNewEndDate] = React.useState<string>('');

    const toggleOpen = () => {
        if (!open && history.length === 0) {
            getHistory(branch, [urlDetail.url.id]).then(setHistory).catch(console.error);
        }
        setOpen(!open);
    };

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
            await addURLCategory(branch, newCategoryId, {
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
            await deleteURLCategory(branch, categoryId, urlDetail.url.id);
            onRefresh();
        } catch (e) {
            console.error(e);
        }
    };

    const renderCategories = () => {
        const cats = urlDetail.categories;
        const limit = 4;
        const displayed = cats.slice(0, limit);
        const remaining = cats.length - limit;

        return (
            <Stack component="div" direction="row" spacing={0.5} sx={{ flexWrap: "wrap" }}>
                {displayed.map(c => {
                    const chip = (
                        <Chip
                            key={c.category.id}
                            label={c.category.name}
                            size="small"
                            variant="outlined"
                            icon={c.constraint ? (
                                <AccessTimeIcon sx={{ fontSize: '14px !important' }} />
                            ) : undefined}
                        />
                    );

                    if (c.constraint) {
                        return (
                            <Tooltip key={c.category.id} title={formatConstraint(c.constraint)}>
                                {chip}
                            </Tooltip>
                        );
                    }
                    return chip;
                })}
                {remaining > 0 && (
                    <Chip label={`+${remaining} more tags`} size="small" variant="outlined" />
                )}
            </Stack>
        );
    };

    return (
        <React.Fragment>
            <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={toggleOpen}
                    >
                        {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{urlDetail.url.id}</TableCell>
                <TableCell>{urlDetail.url.url}</TableCell>
                <TableCell>
                    {renderCategories()}
                </TableCell>
                <TableCell align="right">
                    <IconButton aria-label="edit url" onClick={() => onEdit(urlDetail)} size="small">
                        <EditIcon />
                    </IconButton>
                    <IconButton aria-label="delete url" onClick={() => onDelete(urlDetail)} size="small">
                        <DeleteIcon />
                    </IconButton>
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                            <Grid container spacing={2}>
                                <Grid size={7.2}> {/* 60% */}
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
                                                                <IconButton
                                                                    size="small"
                                                                    onClick={() => handleDeleteMapping(m.category.id)}
                                                                    color="error"
                                                                >
                                                                    <DeleteIcon fontSize="inherit" />
                                                                </IconButton>
                                                            </TableCell>
                                                        </TableRow>
                                                    );
                                                })}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </Grid>
                                <Grid size={4.8}> {/* 40% */}
                                    <Typography variant="h6" gutterBottom component="div">
                                        History
                                    </Typography>
                                    <HistoryTable commits={history} small={true} />
                                </Grid>
                            </Grid>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    )
});

function MatchingListPage() {
    const {currentBranch} = useBranch();
    // State info for the Page
    const [urls, setURLs] = React.useState<IRestURLDetail[]>([]);
    const [categories, setCategories] = React.useState<LUT<ICategory>>({});

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<IRestURLDetail[]>([]);
    const comparator = React.useCallback((a: IRestURLDetail, b: IRestURLDetail): number => a.url.url.localeCompare(b.url.url), []);
    const [quickSearch, setQuickSearch] = React.useState<SearchParser | null>(null);
    // Memoize the filtered rows to avoid unnecessary recalculations
    const filteredRows = React.useMemo(
        () => urls.filter(x => {
            return quickSearch?.test(KVaddRAW(URLMappingToKV(x))) ?? true;
        }),
        [quickSearch, urls],
    );

    // Memoize the download rows to avoid unnecessary transformations
    const downloadRows = React.useMemo(
        () => filteredRows.map(row => URLMappingToKV(row)),
        [filteredRows],
    );

    // Load urls From backend
    const fetchData = React.useCallback(() => {
        Promise.all([getURLs(currentBranch), getCategories(currentBranch)])
            .then(([urlsData, categoriesData]) => {
                setURLs(urlsData);
                setCategories(buildLUTFromID(categoriesData));
            })
            .catch((error) => console.error("Error:", error));
    }, [currentBranch]);

    React.useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Edit Dialog State
    const [editURL, setEditURL] = React.useState<TriState<IRestURLDetail>>(TriState.CLOSED);
    const handleEditOpen = React.useCallback((url: IRestURLDetail | null = null) => {
        setEditURL(url ? new TriState(url) : TriState.NEW);
    }, []);
    const handleEditDialogClose = () => {
        setEditURL(TriState.CLOSED);
    };

    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<IRestURLDetail | null>(null);
    const handleDelete = React.useCallback((url: IRestURLDetail) => {
        setDeleteDialogOpen(url);
    }, []);
    const handleDeleteConfirmation = (del: boolean) => {
        if (del && isDeleteDialogOpen != null) {
            deleteURL(currentBranch, isDeleteDialogOpen.url.id).then(() => {
                fetchData();
            });
        }
        setDeleteDialogOpen(null);
    }

    const handleSave = async (id: string | null, urlValue: string) => {
        if (id == null) {
            // create new URL
            await createURL(currentBranch, urlValue);
        } else {
            // update existing URL
            await updateURL(currentBranch, id, urlValue);
        }
        fetchData();
        handleEditDialogClose();
    };

    return (
        <>
            <Grid
                container
                spacing={1}
                sx={{ justifyContent: "center", alignItems: "center" }}
            >
                <ListHeader
                    onCreate={() => handleEditOpen()}
                    setQuickSearch={setQuickSearch}
                    addElement={"URL"}
                    downloadRows={downloadRows}
                    availableFields={UrlMappingFieldsRaw}
                />
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper} style={{maxHeight: 'calc(100vh - 190px)', overflow: 'auto'}}>
                            <Table sx={{ minWidth: 650 }} size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell style={{ width: 40 }} />
                                        <TableCell>ID</TableCell>
                                        <TableCell>URL</TableCell>
                                        <TableCell>Categories</TableCell>
                                        <TableCell align="right"></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map(urlMap =>
                                        <BuildRow
                                            key={urlMap.url.id}
                                            urlDetail={urlMap}
                                            branch={currentBranch}
                                            onEdit={handleEditOpen}
                                            onDelete={handleDelete}
                                            categories={categories}
                                            onRefresh={fetchData}
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
                header={"Delete URL?"}
                body={"Are you sure you want to Delete the URL? This will also remove it from all categories."}
                isOpen={isDeleteDialogOpen != null}
            />
            <EditDialog
                urlDetail={editURL}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

interface EditDialogProps {
    urlDetail: TriState<IRestURLDetail>,
    onClose: () => void,
    onSave: (id: string | null, url: string) => void,
}
function EditDialog(props: EditDialogProps) {
    const { urlDetail, onClose, onSave } = props;

    const [url, setUrl] = React.useState('');

    // validate inputs
    const urlError: string|null = React.useMemo(
        () => simpleStringCheck(url),
        [url],
    );

    React.useEffect(() => {
        if (!urlDetail.isNull()) {
            setUrl(urlDetail.getValue()!.url.url);
        } else {
            setUrl("");
        }
    }, [urlDetail]);

    const handleSave = () => {
        if (urlError != null) {
            // only continue if the inputs are valid
            return;
        }

        onSave(urlDetail.getValue()?.url.id ?? null, url);
    };

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleSave();
        }
    };

    return (
        <Dialog open={urlDetail.isOpen()} onClose={onClose} onKeyDown={handleKeyDown}>
            <DialogTitle>{urlDetail.getValue() ? 'Edit URL' : 'Add URL'}</DialogTitle>
            <DialogContent>
                <Box component="div" sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
                    <TextField
                        label="URL"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        error={urlError != null}
                        helperText={urlError ? urlError : ''}
                        required
                        fullWidth
                    />
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleSave} disabled={urlError != null}>Save</Button>
                <Button onClick={onClose}>Cancel</Button>
            </DialogActions>
        </Dialog>
    );
}

export default MatchingListPage;

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
    Tabs,
    Tab,
    Divider,
    Accordion,
    AccordionSummary,
    AccordionDetails,
} from "@mui/material";
import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import TimelineOppositeContent from '@mui/lab/TimelineOppositeContent';
import Grid from '@mui/material/Grid';
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HistoryIcon from '@mui/icons-material/History';
import CategoryIcon from '@mui/icons-material/Category';
import OpenInFullIcon from '@mui/icons-material/OpenInFull';
import TimelineIcon from '@mui/icons-material/Timeline';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

import {createURL, deleteURL, getURLs, updateURL} from "../api/url"
import {addURLCategory, deleteURLCategory} from "../api/mapping"
import {ListHeader} from "./shared/ListHeader";
import {MyPaginator} from "./shared/MyPaginator";
import {SearchParser} from "../searchParser";
import {getHistory} from "../api/history";
import {KVaddRAW} from "../types/stringKV";
import { useBranch } from "../hooks/useBranch";
import {IRestURLDetail, UrlMappingFieldsRaw, URLMappingToKV, IURLCreateInput, IURLUpdateInput} from "../types/url";
import HistoryTable from "./shared/HistoryTable";
import {IRestCommit} from "../types/history";
import {TriState} from "../types/EditDialogState";
import {ConfirmDeletionDialog} from "./shared/ConfirmDeletionDialog";
import {getCategories} from "../api/category";
import {UrlCategoryMappings} from "./shared/UrlCategoryMappings";
import {ICategory} from "../types/category";
import {CategoryChip} from "./shared/CategoryChip";
import {formatConstraint, formatUnixTimestamp, formatUnixDateOnly} from "../util/DateString";
import {simpleStringCheck} from "../util/InputValidators";
import {useAuth} from "../hooks/useLogin";
import {buildLUTFromID, LUT} from "../types/LookUpTable";

interface BuildRowProps {
    urlDetail: IRestURLDetail,
    branch: string,
    isLocked: boolean,
    onEdit: (url: IRestURLDetail) => void,
    onDelete: (url: IRestURLDetail) => void,
    categories: LUT<ICategory>,
    onRefresh: () => void,
    index: number,
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
    const { urlDetail, branch, isLocked, onEdit, onDelete, categories, onRefresh, index } = props;
    const authMgmt = useAuth();

    const [open, setOpen] = React.useState(false);
    const [history, setHistory] = React.useState<IRestCommit[]>([]);
    const [tabValue, setTabValue] = React.useState(0);

    const toggleOpen = () => {
        if (!open && history.length === 0) {
            getHistory(authMgmt.token, branch, [urlDetail.url.id])
                .then(setHistory)
                .catch(err => console.error('Failed to load history:', err));
        }
        setOpen(prev => !prev);
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
                        <CategoryChip
                            key={c.category.id}
                            category={c.category}
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

    const renderExperimentalContent = () => {
        const mappings = (
            <UrlCategoryMappings
                urlDetail={urlDetail}
                isLocked={isLocked}
                categories={categories}
                onRefresh={onRefresh}
            />
        );

        const timeline = (
            <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TimelineIcon fontSize="small" /> Activity Timeline
                </Typography>
                {history.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                        No history available for this URL.
                    </Typography>
                ) : (
                    <Timeline position="right" sx={{ p: 0, m: 0 }}>
                        {history.map((commit, i) => (
                            <TimelineItem key={commit.uuid}>
                                <TimelineOppositeContent sx={{ py: '12px', px: 2, flex: 0.15, minWidth: 120 }}>
                                    <Typography variant="caption" color="text.secondary">
                                        {formatUnixTimestamp(commit.created_at)}
                                    </Typography>
                                </TimelineOppositeContent>
                                <TimelineSeparator>
                                    <TimelineDot color="primary" variant="outlined" />
                                    {i < history.length - 1 && <TimelineConnector />}
                                </TimelineSeparator>
                                <TimelineContent sx={{ py: '12px', px: 2 }}>
                                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                        {commit.author}
                                    </Typography>
                                    <Typography variant="body2">{commit.description}</Typography>
                                </TimelineContent>
                            </TimelineItem>
                        ))}
                    </Timeline>
                )}
            </Box>
        );

        return (
            <Paper variant="outlined" sx={{ width: '100%', mb: 1 }}>
                <Tabs
                    value={tabValue}
                    onChange={(_, v) => setTabValue(v)}
                    sx={{ borderBottom: 1, borderColor: 'divider', px: 2, bgcolor: 'grey.50' }}
                >
                    <Tab icon={<CategoryIcon />} label="Mappings" iconPosition="start" />
                    <Tab icon={<HistoryIcon />} label="History" iconPosition="start" />
                </Tabs>
                <Box sx={{ minHeight: 200 }}>
                    {tabValue === 0 ? mappings : timeline}
                </Box>
            </Paper>
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
                <TableCell>{urlDetail.url.description}</TableCell>
                <TableCell>
                    {renderCategories()}
                </TableCell>
                <TableCell align="right">
                    {!isLocked && (
                        <>
                            <IconButton aria-label="edit url" onClick={() => onEdit(urlDetail)} size="small">
                                <EditIcon />
                            </IconButton>
                            <IconButton aria-label="delete url" onClick={() => onDelete(urlDetail)} size="small">
                                <DeleteIcon />
                            </IconButton>
                        </>
                    )}
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0, paddingRight: 0 }} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ 
                            ml: 2, 
                            mr: 0, 
                            mb: 2, 
                            mt: 1, 
                            borderLeft: '4px solid', 
                            borderColor: 'primary.main',
                            pl: 2
                        }}>
                            {renderExperimentalContent()}
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    )
});

function MatchingListPage() {
    const authMgmt = useAuth();
    const {currentBranch, isLocked} = useBranch();

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
        Promise.all([getURLs(authMgmt.token, currentBranch), getCategories(authMgmt.token, currentBranch)])
            .then(([urlsData, categoriesData]) => {
                setURLs(urlsData);
                setCategories(buildLUTFromID(categoriesData));
            })
            .catch((error) => console.error("Error:", error));
    }, [currentBranch]);

    React.useEffect(() => {
        fetchData();
    }, [fetchData]);

    const [editURL, setEditURL] = React.useState<TriState<IRestURLDetail>>(TriState.CLOSED);
    const handleEditOpen = React.useCallback((url: IRestURLDetail | null = null) => {
        setEditURL(url ? new TriState(url) : TriState.NEW);
    }, []);
    const handleEditDialogClose = React.useCallback(() => {
        setEditURL(TriState.CLOSED);
    }, []);

    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<IRestURLDetail | null>(null);
    const handleDelete = React.useCallback((url: IRestURLDetail) => {
        setDeleteDialogOpen(url);
    }, []);

    const handleDeleteConfirmation = async (del: boolean) => {
        if (del && isDeleteDialogOpen != null) {
            await deleteURL(authMgmt.token, isDeleteDialogOpen.url.id);
            fetchData();
        }
        setDeleteDialogOpen(null);
    };

    const handleSave = async (id: string | null, urlValue: string, description: string) => {
        if (id == null) {
            // create new URL
            await createURL(authMgmt.token, {url: urlValue, description});
        } else {
            // update existing URL
            await updateURL(authMgmt.token, id, {url: urlValue, description});
        }
        fetchData();
        handleEditDialogClose();
    };

    return (
        <>
            <Grid
                container
                spacing={1}
                sx={{ justifyContent: "center" }}
            >
                <Grid size={12}>
                    <ListHeader
                        onCreate={() => handleEditOpen()}
                        setQuickSearch={setQuickSearch}
                        addElement={"URL"}
                        downloadRows={downloadRows}
                        availableFields={UrlMappingFieldsRaw}
                        isLocked={isLocked}
                    />
                </Grid>
                <Grid size={12}>
                    <Paper>
                        <TableContainer component={Paper} style={{maxHeight: 'calc(100vh - 190px)', overflow: 'auto'}}>
                            <Table sx={{ minWidth: 650 }} size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell style={{ width: 40 }} />
                                        <TableCell>ID</TableCell>
                                        <TableCell>URL</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell>Categories</TableCell>
                                        <TableCell align="right"></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map((urlMap, index) =>
                                        <BuildRow
                                            key={urlMap.url.id}
                                            urlDetail={urlMap}
                                            branch={currentBranch}
                                            isLocked={isLocked}
                                            onEdit={handleEditOpen}
                                            onDelete={handleDelete}
                                            categories={categories}
                                            onRefresh={fetchData}
                                            index={index}
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
    onSave: (id: string | null, url: string, description: string) => void,
}
function EditDialog(props: EditDialogProps) {
    const { urlDetail, onClose, onSave } = props;

    const [url, setUrl] = React.useState('');
    const [description, setDescription] = React.useState('');

    // validate inputs
    const urlError: string|null = React.useMemo(
        () => simpleStringCheck(url),
        [url],
    );

    React.useEffect(() => {
        if (!urlDetail.isNull()) {
            setUrl(urlDetail.getValue()!.url.url);
            setDescription(urlDetail.getValue()!.url.description);
        } else {
            setUrl("");
            setDescription("");
        }
    }, [urlDetail]);

    const handleSave = () => {
        if (urlError != null) {
            // only continue if the inputs are valid
            return;
        }

        onSave(urlDetail.getValue()?.url.id ?? null, url, description);
    };

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleSave();
        }
    };

    return (
        <Dialog open={urlDetail.isOpen()} onClose={onClose} onKeyDown={handleKeyDown}>
            <DialogTitle>{urlDetail.isNew() ? 'Add URL' : 'Edit URL'}</DialogTitle>
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
                    <TextField
                        label="Description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        required
                        fullWidth
                        multiline
                        rows={2}
                    />
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button onClick={handleSave} disabled={urlError != null} variant="contained">Save</Button>
            </DialogActions>
        </Dialog>
    );
}

export default MatchingListPage;

import React from 'react';
import {getCategories, ICategory} from "../api/categories";
import {
    getURLs,
    IURL,
    IMutableURL,
    deleteURL,
    createURL,
    updateURL,
    setURLCategory
} from "../api/urls"
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import IconButton from "@mui/material/IconButton";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import Paper from '@mui/material/Paper';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Collapse from '@mui/material/Collapse';
import Autocomplete from '@mui/material/Autocomplete';
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Modal from '@mui/material/Modal'
import Chip from '@mui/material/Chip'
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import {colors} from "../util/colormixer";
import TablePagination from '@mui/material/TablePagination';
import {buildLUTFromID, getLUTValues, LUT} from "../util/LookUpTable";
import DeleteIcon from "@mui/icons-material/Delete";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";

const COMPARATORS = {
    BY_ID:  (a: IURL, b: IURL) => a.id - b.id
};

const ModalStyle = {
    position: 'absolute' as 'absolute',
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
    url: IURL,
    categories: LUT<ICategory>,
    onDelete: () => void,
}) {
    const {
        url,
        categories,
        onDelete,
    } = props;

    // (un)fold a row into multiple rows
    const [isOpen, setIsOpen] = React.useState(false);

    const [isCategories, setCategories] = React.useState(url.categories);

    // helper function, triggered when category selector changes
    const handleChange = (event: React.SyntheticEvent, cats: ICategory[]) => {
        if (Array.isArray(cats)) {
            // update api
            setURLCategory(url.id, cats.map(c => c.id)).then(newCats => {
                // save new version
                setCategories(newCats);
            });
            /* old version
            const { added, removed } = CompareLists(isCategories, cats.map(c => c.id));

            added.forEach(cat => addURLCategory(url.id, cat));
            removed.forEach(cat => deleteURLCategory(url.id, cat));

            setCategories(cats.map(c => c.id));
             */
        }
    };

    return (
        <React.Fragment>
            <TableRow key={url.id}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{url.id}</TableCell>
                <TableCell>{url.hostname}</TableCell>
                <TableCell>
                    <Autocomplete
                        multiple
                        disableCloseOnSelect
                        size="small"
                        options={getLUTValues(categories)}
                        getOptionLabel={(cat) => cat.name}
                        defaultValue={isCategories.map(c => categories[c])}
                        onChange={handleChange}
                        renderTags={(values, getTagProps) =>
                            values.map((val, index: number) => {
                                const { key, ...tagProps } = getTagProps({ index });
                                return (
                                    <Chip variant="outlined" label={val.name} key={key} {...tagProps} sx={{ bgcolor: colors[val.color]}} />
                                );
                            })
                        }
                        isOptionEqualToValue={(a, b) => a.id === b.id}
                        renderOption={(props, option, { selected }) => {
                            const { key, ...optionProps } = props;
                            return (
                                <li key={key} {...optionProps}>
                                    <Box
                                        component="span"
                                        sx={{
                                            width: 14,
                                            height: 14,
                                            flexShrink: 0,
                                            borderRadius: '3px',
                                            mr: 1,
                                            mt: '2px',
                                        }}
                                        style={{ backgroundColor: colors[option.color] }}
                                    />
                                    <Box
                                        sx={(t) => ({
                                            flexGrow: 1,
                                            '& span': {
                                                color: '#8b949e',
                                                ...t.applyStyles('light', {
                                                    color: '#586069',
                                                }),
                                            },
                                        })}
                                    >
                                        {option.name}
                                    </Box>
                                </li>
                            );
                        }}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                variant="standard"
                                placeholder="Categories"
                            />
                        )}
                    />
                </TableCell>
                <TableCell><DeleteIcon onClick={onDelete}/></TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0}} colSpan={4}>
                    <Collapse in={isOpen} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1}} >
                            <Typography variant="h6" gutterBottom component="div">
                                History
                            </Typography>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
            </React.Fragment>
    )
}

function MatchingListPage() {
    const [urls, setURLs] = React.useState<IURL[]>([]);
    const [categories, setCategory] = React.useState<LUT<ICategory>>([]);
    const [editURL, setEditURL] = React.useState<IURL | null>(null);
    const [isEditDialogOpen, setEditDialogOpen] = React.useState(false);
    const [isModalOpen, setModalOpen] = React.useState<boolean>(false);

    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(50);
    const [comparator, setComparator] = React.useState(() => COMPARATORS.BY_ID);
    const [quickSearch, setQuickSearch] = React.useState('');

    const handleChangePage = (_event: unknown, newPage: number) => setPage(newPage);
    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const filteredRows = React.useMemo(
        () =>
            urls.filter(x => {
                // not sure if switching to sth. like "levenshtein distance" makes more sense?
                return `${x.id} ${x.hostname} ${x.categories.map(c => categories[c].name).join(' ')}`.toLowerCase().includes(quickSearch.toLowerCase())
            }),
        [quickSearch, urls, categories],
    );
    const visibleRows = React.useMemo(
        () =>
            filteredRows.sort(comparator).slice(
                page * rowsPerPage,
                page * rowsPerPage + rowsPerPage,
            ),
        [comparator, filteredRows, page, rowsPerPage],
    );

    React.useEffect(() => {
        Promise.all([getURLs(), getCategories()])
            .then(([urlsData, categoriesData]) => {
                setCategory(buildLUTFromID(categoriesData));
                setURLs(urlsData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    const handleDelete = (remove_url: IURL) => {
        deleteURL(remove_url.id).then(() => {
            // remove URL with ID from store
            setURLs(urls.filter(uri => uri.id !== remove_url.id));
        });
    }

    const handleEditOpen = (uri: IURL | null) => {
        setEditURL(uri);
        setEditDialogOpen(true);
    };

    const handleEditDialogClose = () => {
        setEditDialogOpen(false);
    };

    const handleSave = (urlID: number|null, uri: IMutableURL) => {
        if (urlID == null) {
            // add new URL
            createURL(uri).then(newURI => {
                setURLs([...urls, newURI]);
            });
        } else {
            updateURL(urlID, uri).then(newURI => {
                // "replace" existing URL if id matches
                setURLs(urls.map(u => u.id === urlID ? newURI : u));
            })
        }
        handleEditDialogClose();
    };

    return (
        <>
            <Paper sx={{ width: '100%', mb: 2 }}>
            <div>
                <TextField label="Quick Search" size="small" variant="standard" onChange={event => setQuickSearch(event.target.value)}/>
            </div>
            <Button onClick={() => handleEditOpen(null)}>
                + Add Category
            </Button>
            <TableContainer component={Paper} style={{maxHeight: '100%'}}>
                <Modal
                    open={isModalOpen}
                        onClose={() => setModalOpen(false)}
                        aria-labelledby="modal-modal-title"
                        aria-describedby="modal-modal-description"
                    >
                        <Box sx={ModalStyle}>
                            <Typography id="modal-modal-title" variant="h6" component="h2">
                                Text in a modal
                            </Typography>
                            <Typography id="modal-modal-description" sx={{ mt: 2 }}>
                                Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
                            </Typography>
                        </Box>
                    </Modal>
                <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table" stickyHeader>
                    <TableHead>
                    <TableRow>
                        <TableCell />
                        <TableCell><Stack direction="row"><Typography>ID</Typography><FilterAltIcon onClick={() => setModalOpen(true)}/></Stack></TableCell>
                        <TableCell><Stack direction="row"><Typography>Hostname</Typography><FilterAltIcon onClick={() => setModalOpen(true)}/></Stack></TableCell>
                        <TableCell><Stack direction="row"><Typography>Categories</Typography><FilterAltIcon onClick={() => setModalOpen(true)}/></Stack></TableCell>
                        <TableCell></TableCell>
                    </TableRow>
                    </TableHead>
                    <TableBody>
                    {visibleRows.map(url =>
                        <BuildRow
                            key={url.id}
                            url={url}
                            categories={categories}
                            onDelete={() => handleDelete(url)}
                        />
                    )}
                    </TableBody>
                </Table>
                </TableContainer>
                <TablePagination
                    rowsPerPageOptions={[20, 50, 100]}
                    component="div"
                    count={filteredRows.length}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />
            </Paper>
            <EditDialog
                isOpen={isEditDialogOpen}
                uri={editURL}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

function EditDialog(props: {
    isOpen: boolean,
    uri: IURL | null,
    onClose: () => void,
    onSave: (id: number | null, uri: IMutableURL) => void
}) {
    let {isOpen, uri, onClose, onSave} = props;

    const [hostname, setHostname] = React.useState('');

    React.useEffect(() => {
        if (uri) {
            setHostname(uri.hostname);
        } else {
            setHostname("")
        }
    }, [uri]);

    const handleSave = () => {
        onSave(uri?.id ?? null, {hostname});
        setHostname("")
    };

    return (
        <Dialog open={isOpen} onClose={onClose}>
            <DialogTitle>Edit URL</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                    <TextField label="Hostname (FQDN)" value={hostname} onChange={(e) => setHostname(e.target.value)}/>
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleSave}>Save</Button>
                <Button onClick={onClose}>Cancel</Button>
            </DialogActions>
        </Dialog>
    );
}

export default MatchingListPage;

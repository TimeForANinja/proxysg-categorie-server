import React from 'react';
import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from "@mui/material";
import Grid from '@mui/material/Grid';

import { createURL, deleteURL, getURLs, updateURL } from "../../api/url"
import { ListHeader } from "../shared/ListHeader";
import { MyPaginator } from "../shared/MyPaginator";
import { SearchParser } from "../../searchParser";
import { KVaddRAW } from "../../types/stringKV";
import { useBranch } from "../../hooks/useBranch";
import { useNotification } from "../../hooks/useNotification";
import { IRestURLDetail, UrlMappingFieldsRaw, URLMappingToKV } from "../../types/url";
import { TriState } from "../../types/EditDialogState";
import { ConfirmDeletionDialog } from "../shared/ConfirmDeletionDialog";
import { getCategories } from "../../api/category";
import { ICategory } from "../../types/category";
import { useAuth } from "../../hooks/useLogin";
import { buildLUTFromID, LUT } from "../../types/LookUpTable";

import { UrlRow } from "./UrlRow";
import { UrlEditDialog } from "./UrlEditDialog";

export default function MatchingListPage() {
    const authMgmt = useAuth();
    const { showError, showSuccess } = useNotification();
    const { currentBranch, isLocked } = useBranch();

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
        Promise.all([getURLs(authMgmt.token, currentBranch, true, true), getCategories(authMgmt.token, currentBranch, false)])
            .then(([urlsData, categoriesData]) => {
                setURLs(urlsData);
                setCategories(buildLUTFromID(categoriesData.map(x => x.category)));
            })
            .catch((error) => showError(error.message));
    }, [authMgmt.token, currentBranch, showError]);

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
            try {
                await deleteURL(authMgmt.token, isDeleteDialogOpen.url.id);
                showSuccess("URL deleted successfully");
                fetchData();
            } catch (e: any) {
                showError(e.message);
            }
        }
        setDeleteDialogOpen(null);
    };

    const handleSave = async (id: string | null, urlValue: string, description: string) => {
        try {
            if (id == null) {
                await createURL(authMgmt.token, { url: urlValue, description });
                showSuccess("URL created successfully");
            } else {
                await updateURL(authMgmt.token, id, { url: urlValue, description });
                showSuccess("URL updated successfully");
            }
            fetchData();
            handleEditDialogClose();
        } catch (e: any) {
            showError(e.message);
        }
    };

    return (
        <>
            <Grid container spacing={1} sx={{ justifyContent: "center" }}>
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
                        <TableContainer component={Paper} style={{ maxHeight: 'calc(100vh - 190px)', overflow: 'auto' }}>
                            <Table sx={{ minWidth: 650, '& .MuiTableCell-root': { fontFamily: 'monospace' } }} size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell style={{ width: 40 }} />
                                        <TableCell>ID</TableCell>
                                        <TableCell>URL</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell>Categories</TableCell>
                                        <TableCell>BC Categories</TableCell>
                                        <TableCell align="right"></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map((urlMap) =>
                                        <UrlRow
                                            key={urlMap.url.id}
                                            urlDetail={urlMap}
                                            branch={currentBranch}
                                            isLocked={isLocked}
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
            <UrlEditDialog
                urlDetail={editURL}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

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
import Grid from "@mui/material/Grid";

import {
    createCategory,
    deleteCategory,
    getCategories,
    updateCategory,
} from "../../api/category";
import { ListHeader } from "../shared/ListHeader";
import { ConfirmDeletionDialog } from "../shared/ConfirmDeletionDialog";
import { TriState } from "../../types/EditDialogState";
import { MyPaginator } from "../shared/MyPaginator";
import {buildLUTFromGetter, LUT} from "../../types/LookUpTable";
import { SearchParser } from "../../searchParser";
import {CategoryFieldsRaw, CategoryToKV, ICategory, IRestCategoryDetail} from "../../types/category";
import { KVaddRAW } from "../../types/stringKV";
import { useBranch } from "../../hooks/useBranch";
import { useNotification } from "../../hooks/useNotification";
import { useAuth } from "../../hooks/useLogin";

import { CategoryRow } from "./CategoryRow";
import { CategoryEditDialog } from "./CategoryEditDialog";

export default function CategoryListPage() {
    const authMgmt = useAuth();
    const { showError, showSuccess } = useNotification();
    const { currentBranch, isLocked } = useBranch();

    // State info for the Page
    const [categories, setCategories] = React.useState<LUT<IRestCategoryDetail>>({});

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<IRestCategoryDetail[]>([]);
    const comparator = React.useCallback((a: IRestCategoryDetail, b: IRestCategoryDetail): number => a.category.name.localeCompare(b.category.name), []);
    const [quickSearch, setQuickSearch] = React.useState<SearchParser | null>(null);

    // Memoize the filtered rows to avoid unnecessary recalculations
    const filteredRows = React.useMemo(
        () => Object.values(categories).filter(x => {
            return quickSearch?.test(KVaddRAW(CategoryToKV(x))) ?? true;
        }),
        [quickSearch, categories],
    );

    // Memoize the download rows to avoid unnecessary transformations
    const downloadRows = React.useMemo(
        () => filteredRows.map(row => CategoryToKV(row)),
        [filteredRows],
    );

    // Load categories From backend
    const fetchData = React.useCallback(() => {
        getCategories(authMgmt.token, currentBranch, true)
            .then((categoriesData) => {
                setCategories(buildLUTFromGetter(categoriesData, (c) => c.category.id));
            })
            .catch((error) => showError(error.message));
    }, [authMgmt.token, currentBranch, showError]);

    React.useEffect(() => {
        fetchData();
    }, [fetchData]);

    const [editCategory, setEditCategory] = React.useState<TriState<ICategory>>(TriState.CLOSED);
    const handleEditOpen = React.useCallback((cat: ICategory | null = null) => {
        setEditCategory(cat ? new TriState(cat) : TriState.NEW);
    }, []);
    const handleEditDialogClose = React.useCallback(() => {
        setEditCategory(TriState.CLOSED);
    }, []);

    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<ICategory | null>(null);
    const handleDelete = React.useCallback((cat: ICategory) => {
        setDeleteDialogOpen(cat);
    }, []);

    const handleDeleteConfirmation = async (del: boolean) => {
        if (del && isDeleteDialogOpen != null) {
            try {
                await deleteCategory(authMgmt.token, isDeleteDialogOpen.id);
                showSuccess("Category deleted successfully");
                fetchData();
            } catch (e: any) {
                showError(e.message);
            }
        }
        setDeleteDialogOpen(null);
    };

    const handleSave = async (id: string | null, name: string, description: string, color: number) => {
        try {
            if (id == null) {
                await createCategory(authMgmt.token, { name, description, color });
                showSuccess("Category created successfully");
            } else {
                await updateCategory(authMgmt.token, id, { name, description, color });
                showSuccess("Category updated successfully");
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
                        addElement={"Category"}
                        downloadRows={downloadRows}
                        availableFields={CategoryFieldsRaw}
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
                                        <TableCell>Name</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell />
                                        <TableCell>Children</TableCell>
                                        <TableCell align="right"></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map((row) =>
                                        <CategoryRow
                                            key={row.category.id}
                                            category={row}
                                            categories={categories}
                                            branch={currentBranch}
                                            isLocked={isLocked}
                                            onEdit={handleEditOpen}
                                            onDelete={handleDelete}
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
                header={"Delete Category?"}
                body={"Are you sure you want to Delete the Category? This will NOT remove the URLs associated with it."}
                isOpen={isDeleteDialogOpen != null}
            />
            <CategoryEditDialog
                categoryDetail={editCategory}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

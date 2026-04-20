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
import { buildLUTFromID, LUT } from "../../types/LookUpTable";
import { SearchParser } from "../../searchParser";
import { CategoryFieldsRaw, CategoryToKV, ICategory } from "../../types/category";
import { KVaddRAW } from "../../types/stringKV";
import { useBranch } from "../../hooks/useBranch";
import { useAuth } from "../../hooks/useLogin";

import { CategoryRow } from "./CategoryRow";
import { CategoryEditDialog } from "./CategoryEditDialog";

export default function CategoryListPage() {
    const authMgmt = useAuth();
    const { currentBranch, isLocked } = useBranch();

    // State info for the Page
    const [categories, setCategories] = React.useState<LUT<ICategory>>({});

    // search and pagination
    const [visibleRows, setVisibleRows] = React.useState<ICategory[]>([]);
    const comparator = React.useCallback((a: ICategory, b: ICategory): number => a.name.localeCompare(b.name), []);
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
        getCategories(authMgmt.token, currentBranch)
            .then((categoriesData) => {
                setCategories(buildLUTFromID(categoriesData));
            })
            .catch((error) => console.error("Error:", error));
    }, [authMgmt.token, currentBranch]);

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
            await deleteCategory(authMgmt.token, isDeleteDialogOpen.id);
            fetchData();
        }
        setDeleteDialogOpen(null);
    };

    const handleSave = async (id: string | null, name: string, description: string, color: number) => {
        if (id == null) {
            await createCategory(authMgmt.token, { name, description, color });
        } else {
            await updateCategory(authMgmt.token, id, { name, description, color });
        }
        fetchData();
        handleEditDialogClose();
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
                            <Table sx={{ minWidth: 650 }} size="small" stickyHeader>
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
                                    {visibleRows.map((cat) =>
                                        <CategoryRow
                                            key={cat.id}
                                            category={cat}
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

import React from 'react';
import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';
import Grid from '@mui/material/Grid';

import { createToken, deleteToken, getTokens, rollToken, updateToken } from "../../api/token";
import { getCategories } from "../../api/category";
import { ListHeader } from "../shared/ListHeader";
import { ConfirmDeletionDialog } from "../shared/ConfirmDeletionDialog";
import { TriState } from "../../types/EditDialogState";
import { MyPaginator } from "../shared/MyPaginator";
import { buildLUTFromID, LUT } from "../../types/LookUpTable";
import { SearchParser } from "../../searchParser";
import {
    IApiToken,
    ApiTokenToKV,
    ApiTokenFieldsRaw,
    IRestTokenDetail
} from '../../types/apiToken';
import { ICategory } from "../../types/category";
import { KVaddRAW } from "../../types/stringKV";
import { useBranch } from "../../hooks/useBranch";
import { useAuth } from "../../hooks/useLogin";

import { ApiTokenRow } from "./ApiTokenRow";
import { ApiTokenEditDialog } from "./ApiTokenEditDialog";

export default function ApiTokensPage() {
    const authMgmt = useAuth();
    const { currentBranch, isLocked } = useBranch();

    const [tokens, setTokens] = React.useState<IRestTokenDetail[]>([]);
    const [categories, setCategories] = React.useState<LUT<ICategory>>({});

    const [visibleRows, setVisibleRows] = React.useState<IRestTokenDetail[]>([]);
    const comparator = React.useCallback((a: IRestTokenDetail, b: IRestTokenDetail): number => a.token.description.localeCompare(b.token.description), []);
    const [quickSearch, setQuickSearch] = React.useState<SearchParser | null>(null);

    const filteredRows = React.useMemo(
        () => tokens.filter(x => {
            return quickSearch?.test(KVaddRAW(ApiTokenToKV(x))) ?? true;
        }),
        [quickSearch, tokens],
    );

    const downloadRows = React.useMemo(
        () => filteredRows.map(row => ApiTokenToKV(row)),
        [filteredRows],
    );

    const fetchData = React.useCallback(() => {
        Promise.all([getTokens(authMgmt.token, currentBranch), getCategories(authMgmt.token, currentBranch)])
            .then(([tokensData, categoriesData]) => {
                setTokens(tokensData);
                setCategories(buildLUTFromID(categoriesData.map(x => x.category)));
            })
            .catch((error) => console.error("Error:", error));
    }, [authMgmt.token, currentBranch]);

    React.useEffect(() => {
        fetchData();
    }, [fetchData]);

    const [editToken, setEditToken] = React.useState<TriState<IApiToken>>(TriState.CLOSED);
    const handleEditOpen = React.useCallback((token: IApiToken | null = null) => {
        setEditToken(token ? new TriState(token) : TriState.NEW);
    }, []);
    const handleEditDialogClose = React.useCallback(() => {
        setEditToken(TriState.CLOSED);
    }, []);

    const [isDeleteDialogOpen, setDeleteDialogOpen] = React.useState<IApiToken | null>(null);
    const handleDelete = React.useCallback((token: IApiToken) => {
        setDeleteDialogOpen(token);
    }, []);

    const handleDeleteConfirmation = async (del: boolean) => {
        if (del && isDeleteDialogOpen != null) {
            await deleteToken(authMgmt.token, isDeleteDialogOpen.id);
            fetchData();
        }
        setDeleteDialogOpen(null);
    };

    const handleRoll = React.useCallback(async (token: IApiToken) => {
        await rollToken(authMgmt.token, token.id);
        fetchData();
    }, [authMgmt.token, fetchData]);

    const handleSave = async (id: string | null, description: string) => {
        if (id == null) {
            await createToken(authMgmt.token, { description });
        } else {
            await updateToken(authMgmt.token, id, { description });
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
                        addElement={"API Token"}
                        downloadRows={downloadRows}
                        availableFields={ApiTokenFieldsRaw}
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
                                        <TableCell>Description</TableCell>
                                        <TableCell>Token Value</TableCell>
                                        <TableCell>Categories</TableCell>
                                        <TableCell align="right"></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {visibleRows.map((tokenDetail) =>
                                        <ApiTokenRow
                                            key={tokenDetail.token.id}
                                            tokenDetail={tokenDetail}
                                            categories={categories}
                                            onEdit={handleEditOpen}
                                            onDelete={handleDelete}
                                            onRoll={handleRoll}
                                            onRefresh={fetchData}
                                            isLocked={isLocked}
                                            branch={currentBranch}
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
                header={"Delete API Token?"}
                body={"Are you sure you want to delete this API Token? Any application using this token will lose access."}
                isOpen={isDeleteDialogOpen != null}
            />
            <ApiTokenEditDialog
                tokenDetail={editToken}
                onClose={handleEditDialogClose}
                onSave={handleSave}
            />
        </>
    );
}

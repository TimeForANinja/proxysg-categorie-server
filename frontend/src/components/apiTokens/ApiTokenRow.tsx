import React from 'react';
import {
    Box,
    Collapse,
    IconButton,
    TableCell,
    TableRow,
    Typography,
    Stack,
} from '@mui/material';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from "@mui/icons-material/Edit";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import RefreshIcon from "@mui/icons-material/Refresh";

import { addTokenCategory, deleteTokenCategory } from "../../api/mapping";
import { getHistory } from "../../api/history";
import { useNotification } from "../../hooks/useNotification";
import { CategoryPicker } from "../shared/CategoryPicker";
import { IApiToken, IRestTokenDetail } from '../../types/apiToken';
import { ICategory } from "../../types/category";
import { IRestCommit } from "../../types/history";
import { LUT } from "../../types/LookUpTable";
import { useAuth } from "../../hooks/useLogin";
import HistoryTable from "../shared/HistoryTable";
import {short_uuid} from "../../util/uuid";
import {formatUnixTimestamp} from "../../util/DateString";

const TIME_SECONDS = 1000;

export interface ApiTokenRowProps {
    tokenDetail: IRestTokenDetail,
    categories: LUT<ICategory>,
    onEdit: (token: IApiToken) => void,
    onDelete: (token: IApiToken) => void,
    onRoll: (token: IApiToken) => void,
    onRefresh: () => void,
    isLocked: boolean,
    branch: string,
}

export const ApiTokenRow = React.memo(function ApiTokenRow(props: ApiTokenRowProps) {
    const {
        tokenDetail,
        categories,
        onEdit,
        onDelete,
        onRoll,
        onRefresh,
        isLocked,
        branch,
    } = props;
    const authMgmt = useAuth();
    const { showError, showSuccess } = useNotification();

    const token = tokenDetail.token;

    const [open, setOpen] = React.useState(false);
    const [history, setHistory] = React.useState<IRestCommit[]>([]);

    const [hideToken, setHideToken] = React.useState(true);
    const [isCopied, setIsCopied] = React.useState(false);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(`${window.location.origin}/api/compile/${token.token_value}`);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 1.5 * TIME_SECONDS);
    };

    const toggleOpen = () => {
        if (!open && history.length === 0) {
            getHistory(authMgmt.token, branch, [token.id])
                .then(setHistory)
                .catch(err => showError(err.message || 'Failed to load history'));
        }
        setOpen(prev => !prev);
    };

    const handleAddCategory = async (cat: ICategory) => {
        try {
            await addTokenCategory(authMgmt.token, token.id, cat.id);
            showSuccess(`Category "${cat.name}" added to token`);
            onRefresh();
        } catch (e: any) {
            showError(e.message);
        }
    };

    const handleDeleteCategory = async (cat: ICategory) => {
        try {
            await deleteTokenCategory(authMgmt.token, token.id, cat.id);
            showSuccess(`Category "${cat.name}" removed from token`);
            onRefresh();
        } catch (e: any) {
            showError(e.message);
        }
    };

    return (
        <React.Fragment>
            <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
                <TableCell>
                    <IconButton aria-label="expand row" size="small" onClick={toggleOpen}>
                        {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{short_uuid(token.id)}</TableCell>
                <TableCell>{token.description}</TableCell>
                <TableCell sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{
                        fontFamily: 'monospace',
                        bgcolor: 'grey.100',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        mr: 1,
                        minWidth: '200px',
                        filter: hideToken ? 'blur(5px)' : 'none',
                        transition: 'filter 0.2s'
                    }}>
                        {token.token_value}
                    </Box>
                    <IconButton size="small" onClick={() => setHideToken(!hideToken)}>
                        {hideToken ? <VisibilityIcon fontSize="small" /> : <VisibilityOffIcon fontSize="small" />}
                    </IconButton>
                    <IconButton size="small" onClick={handleCopy} color={isCopied ? "success" : "default"}>
                        {isCopied ? <CheckIcon fontSize="small" /> : <ContentCopyIcon fontSize="small" />}
                    </IconButton>
                    {!isLocked && (
                        <IconButton aria-label="roll token" onClick={() => onRoll(token)} size="small">
                            <RefreshIcon />
                        </IconButton>
                    )}
                </TableCell>
                <TableCell>
                    {formatUnixTimestamp(tokenDetail.last_used)}
                </TableCell>
                <TableCell>
                    <CategoryPicker
                        categories={categories}
                        isCategories={tokenDetail.categories}
                        onChange={(newIds, added, removed) => {
                            added.forEach(id => handleAddCategory(categories[id]));
                            removed.forEach(id => handleDeleteCategory(categories[id]));
                        }}
                        disabled={isLocked}
                    />
                </TableCell>
                <TableCell align="right">
                    {!isLocked && (
                        <>
                            <IconButton aria-label="edit token" onClick={() => onEdit(token)} size="small">
                                <EditIcon />
                            </IconButton>
                            <IconButton aria-label="delete token" onClick={() => onDelete(token)} size="small">
                                <DeleteIcon />
                            </IconButton>
                        </>
                    )}
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                            <Stack spacing={2}>
                                <Box>
                                    <Typography variant="subtitle2" gutterBottom>Token History</Typography>
                                    <HistoryTable commits={history} small />
                                </Box>
                            </Stack>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    );
});

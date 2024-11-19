
import React, { useState } from 'react';
import { Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Button, TextField} from '@mui/material';
import {getAPITokens, IApiToken} from "../api/tokens";
import {getCategories, ICategory} from "../api/categories";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import IconButton from '@mui/material/IconButton';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check';
import DeleteIcon from '@mui/icons-material/Delete'
import Select, { SelectChangeEvent } from '@mui/material/Select';
import {colors} from "../api/colormixer";
import MenuItem from "@mui/material/MenuItem";
import Box from "@mui/material/Box";

function BuildRow(props: { token: IApiToken, categories: ICategory[]}) {
    const { token, categories } = props;
    const [isCopied, setIsCopied] = React.useState(false);
    const [hideToken, setHideToken] = React.useState(false);
    const [isCategories, setCategories] = React.useState(categories.filter(category => token.categories.includes(category.id)).map(c => c.id));

    const handleCopy = async () => {
        await navigator.clipboard.writeText(token.token);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 1500);  // Change back after 3 seconds
    };

    const handleChange = (event: SelectChangeEvent<number[]>) => {
        if (Array.isArray(event.target.value)) {
            setCategories(event.target.value);
        }
    };

    return (
            <TableRow
                key={token.id}
                sx={{ '&:last-child td, &:last-child th': {border: 0 }}}
            >
                <TableCell component="th" scope="row">{token.id}</TableCell>
                <TableCell>{token.description}</TableCell>
                <TableCell align="right">
                    {hideToken ? token.token : token.token.replace(/[a-zA-Z0-9]/g, '*')}
                    <IconButton onClick={() => setHideToken(!hideToken)}>
                        { hideToken ? <VisibilityIcon /> : <VisibilityOffIcon /> }
                    </IconButton>
                    <IconButton onClick={() => handleCopy()}>
                        {isCopied ? <CheckIcon/> : <ContentCopyIcon/>}
                    </IconButton>
                </TableCell>
                <TableCell>{ token.lastUse }</TableCell>
                <TableCell align="right">
                    <Select
                        multiple
                        value={isCategories}
                        label="Categories"
                        onChange={handleChange}
                        displayEmpty
                        renderValue={(selected) => selected.map(c => categories.find(cat => cat.id === c)?.name).join(', ')}
                    >
                        {
                            categories.map((cat, catIDX) => {
                                return (
                                    <MenuItem key={catIDX} value={cat.id}>
                                        <div style={{ background: cat.color}}>{cat.name}</div>
                                    </MenuItem>
                                )
                            })
                        }
                    </Select>
                </TableCell>
                <TableCell><DeleteIcon/></TableCell>
            </TableRow>
    )
}

function ApiTokenPage() {
    const [tokens, setTokens] = React.useState<IApiToken[]>([]);
    const [categories, setCategory] = React.useState<ICategory[]>([]);
    const [selectedToken, setSelectedToken] = React.useState<IApiToken | null>(null);
    const [isDialogOpen, setDialogOpen] = React.useState(false);

    React.useEffect(() => {
        Promise.all([ getCategories(), getAPITokens()])
            .then(([categoryData, tokenData]) => {
                setTokens(tokenData);
                setCategory(categoryData)
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    const handleEditOpen = (token: IApiToken) => {
        setSelectedToken(token);
        setDialogOpen(true);
    };

    const handleDialogClose = () => {
        setDialogOpen(false);
    };

    const handleSave = (token: IApiToken) => {
        if (token.id === -1) {
            // add new token
            token.id = Math.max(...tokens.map(t => t.id)) + 1;
            setTokens([...tokens, token]);
        } else {
            // "replace" existing token if id matches
            setTokens(tokens.map(t => t.id === token.id ? token : t));
        }
        setDialogOpen(false);
    };

    return (
        <>
            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
                    <TableHead>
                        <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>Description</TableCell>
                            <TableCell align="right">Token</TableCell>
                            <TableCell>Last Used</TableCell>
                            <TableCell align="right">Categories</TableCell>
                            <TableCell></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {tokens.map(token =>
                            <BuildRow key={token.id} token={token} categories={categories}></BuildRow>
                        )}
                        <TableRow>
                            <TableCell colSpan={5} align="center">
                                <Button onClick={() => handleEditOpen({ id: -1, token: '', description: '', categories: [], lastUse: 'never' })}>
                                    + Add Token
                                </Button>
                            </TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableContainer>
                {selectedToken && (
                <EditDialog
                    isOpen={isDialogOpen}
                    token={selectedToken}
                    onClose={handleDialogClose}
                    onSave={handleSave}
                />
            )}
        </>
    );
}

function EditDialog(props: {
    isOpen: boolean,
    token: IApiToken,
    onClose: () => void,
    onSave: (category: IApiToken) => void
}) {
    const { isOpen, token, onClose, onSave } = props;
    const [description, setDescription] = React.useState(token.description);
    const [tokenStr, setTokenStr] = React.useState(token.token);

    React.useEffect(() => {
        if (token) {
            setDescription(token.description);
            setTokenStr(token.token);
        }
    }, [token]);

    const handleSave = () => {
        onSave({ ...token, description, token: tokenStr });
    };

    return (
        <Dialog open={isOpen} onClose={onClose}>
            <DialogTitle>Edit Category</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                    <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
                    <TextField label="Token" value={tokenStr} onChange={(e) => setTokenStr(e.target.value)} />
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleSave}>Save</Button>
                <Button onClick={onClose}>Cancel</Button>
            </DialogActions>
        </Dialog>
    );
}

export default ApiTokenPage;

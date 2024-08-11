import React from 'react';
import {getAPITokens, IApiToken} from "../api/tokens";
import {getCategories, ICategory} from "../api/categories";
import Select from "react-select";
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

function BuildRow(props: { token: IApiToken, categories: ICategory[]}) {
    const { token, categories } = props;
    const [isCopied, setIsCopied] = React.useState(false);
    const [hideToken, setHideToken] = React.useState(false);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(token.token);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 1500);  // Change back after 3 seconds
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
                <TableCell align="right">
                    <Select
                        defaultValue={categories.filter(category => token.categories.includes(category.id)).map(c => ({ value: c.id, label: c.name }))}
                        isMulti
                        options={categories.map(c => ({ value: c.id, label: c.name }))}
                    />
                </TableCell>
            </TableRow>
    )
}

function ApiTokenPage() {
    const [tokens, setTokens] = React.useState<IApiToken[]>([]);
    const [categories, setCategory] = React.useState<ICategory[]>([]);

    React.useEffect(() => {
        Promise.all([ getCategories(), getAPITokens()])
            .then(([categoryData, tokenData]) => {
                setTokens(tokenData);
                setCategory(categoryData)
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    return (
        <TableContainer component={Paper}>
            <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
                <TableHead>
                    <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell align="right">Token</TableCell>
                        <TableCell align="right">Categories</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {tokens.map(token =>
                        <BuildRow key={token.id} token={token} categories={categories}></BuildRow>
                    )}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default ApiTokenPage;

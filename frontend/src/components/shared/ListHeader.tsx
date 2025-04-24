import React from "react";
import {
    Box,
    TextField,
    Button,
    Alert,
    InputAdornment,
    IconButton,
    TableContainer,
    TableHead,
    Table,
    Paper,
    TableRow,
    TableBody,
    TableCell,
    Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import DownloadIcon from "@mui/icons-material/Download"
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import InfoIcon from '@mui/icons-material/Info';
import {CSVLink} from "react-csv"

import {bracesFunctions, BuildSyntaxTree, SearchParser} from "../../searchParser";
import {formatDateForFilename} from "../../util/DateString";
import {StringKV} from "../../model/types/stringKV";


interface ListHeaderProps {
    onCreate: () => void,
    setQuickSearch: (parser: SearchParser | null) => void,
    addElement: string,
    downloadRows:  StringKV[],
    availableFields?: {field: string, description: string}[],
}
export const ListHeader = (props: ListHeaderProps) => {
    const {
        onCreate,
        setQuickSearch,
        addElement,
        downloadRows,
        availableFields,
    } = props;

    const [myTree, setMyTree] = React.useState<SearchParser | null>(null);
    // propagate changes to the parent component
    React.useEffect(() => setQuickSearch(myTree), [myTree, setQuickSearch]);
    const [treeError, setTreeError] = React.useState<string | null>(null);
    const [isInfoOpen, setIsInfoOpen] = React.useState<boolean>(false);

    const updateSearch = (newStr: string) => {
        let tree: SearchParser | null = null;
        try {
            tree = BuildSyntaxTree(newStr);
            setTreeError(null);
        } catch(e: Error | any) {
            setTreeError(e?.message);
        }
        setMyTree(tree);
    }

    // Initialize (empty) Search
    React.useEffect(() => setMyTree(BuildSyntaxTree("")), [setMyTree]);

    return (
        <>
            { /* Search Bar */ }
            <Grid size={8}>
                <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                    <TextField
                        margin="dense"
                        label="Quick Search"
                        size="small"
                        variant="filled"
                        onChange={event => updateSearch(event.target.value)}
                        slotProps={{
                            input: {
                                endAdornment: <InputAdornment position="end">
                                    <IconButton
                                        aria-label={isInfoOpen ? 'hide Info' : 'display Info'}
                                        onClick={() => setIsInfoOpen(!isInfoOpen)}
                                        edge="end"
                                    >
                                        {isInfoOpen ? <InfoIcon/> : <InfoOutlinedIcon/>}
                                    </IconButton>
                                </InputAdornment>
                            }
                        }}
                    />
                </Box>
            </Grid>
            { /* Add-Button */ }
            <Grid size={3}>
                <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                    <Button
                        variant="outlined"
                        onClick={() => onCreate()}
                    >
                        + Add {addElement}
                    </Button>
                </Box>
            </Grid>
            { /* Download Button for visible rows */ }
            <Grid size={1}>
                <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                    <Button
                        aria-label="delete"
                        color="primary"
                        variant="outlined"
                    >
                        <CSVLink
                            data={downloadRows!}
                            separator={";"}
                            filename={`download_${formatDateForFilename()}.csv`}
                            target="_blank"
                        >
                            <DownloadIcon />
                        </CSVLink>
                    </Button>
                </Box>
            </Grid>
            { /* Search Syntax Error (if any) */ }
            { treeError && (
                <Grid size={12}>
                    <Alert severity="error">Invalid Search: { treeError }</Alert>
                </Grid>
            )}
            { /* Search Syntax Guide & Examples */ }
            { isInfoOpen && (
                <Grid size={12}>
                    <Alert
                        severity="info"
                    >
                        <Grid
                            container
                            spacing={2}
                            justifyContent="center"
                            alignItems="flex-start"
                        >
                            {/* Current Search Tree */}
                            {myTree && (
                                <Grid size={12}>
                                    <Paper elevation={0} sx={{ p: 2, mb: 2, bgcolor: '#f5f5f5' }}>
                                        <Box sx={{ fontWeight: 'bold', mb: 1 }}>Current Search Tree:</Box>
                                        <Box sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                            {myTree.print()}
                                        </Box>
                                    </Paper>
                                </Grid>
                            )}

                            {/* Search Syntax Guide */}
                            <Grid size={12}>
                                <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                                    <Box sx={{ fontWeight: 'bold', mb: 1 }}>Search Syntax Guide</Box>
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="body2">
                                            • Use <code>field=value</code> to search for exact matches (e.g., <code>id=123</code>)
                                        </Typography>
                                        <Typography variant="body2">
                                            • Use <code>AND</code> and <code>OR</code> operators to combine searches (e.g., <code>host=example.com AND cats=news</code>)
                                        </Typography>
                                        <Typography variant="body2">
                                            • Use quotes for phrases with spaces (e.g., <code>"example domain"</code>)
                                        </Typography>
                                        <Typography variant="body2">
                                            • Use functions like <code>abs()</code> for advanced searches
                                        </Typography>
                                    </Box>
                                </Paper>
                            </Grid>

                            {/* Available Fields */}
                            <Grid size={6}>
                                <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
                                    <Box sx={{ fontWeight: 'bold', mb: 1 }}>Available Fields</Box>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Field</TableCell>
                                                    <TableCell>Description</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {availableFields ? (
                                                    availableFields.map((field, index) => (
                                                        <TableRow key={index}>
                                                            <TableCell><code>{field.field}</code></TableCell>
                                                            <TableCell>{field.description}</TableCell>
                                                        </TableRow>
                                                    ))
                                                ) : (
                                                    <>
                                                        <TableRow>
                                                            <TableCell><code>id</code></TableCell>
                                                            <TableCell>URL identifier</TableCell>
                                                        </TableRow>
                                                        <TableRow>
                                                            <TableCell><code>host</code></TableCell>
                                                            <TableCell>Hostname/domain</TableCell>
                                                        </TableRow>
                                                        <TableRow>
                                                            <TableCell><code>description</code></TableCell>
                                                            <TableCell>URL description</TableCell>
                                                        </TableRow>
                                                        <TableRow>
                                                            <TableCell><code>cats</code></TableCell>
                                                            <TableCell>Categories (space-separated)</TableCell>
                                                        </TableRow>
                                                        <TableRow>
                                                            <TableCell><code>bc_cats</code></TableCell>
                                                            <TableCell>Blue Coat categories</TableCell>
                                                        </TableRow>
                                                        <TableRow>
                                                            <TableCell><code>_raw</code></TableCell>
                                                            <TableCell>All fields combined</TableCell>
                                                        </TableRow>
                                                    </>
                                                )}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </Paper>
                            </Grid>

                            {/* Available Functions */}
                            <Grid size={6}>
                                <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
                                    <Box sx={{ fontWeight: 'bold', mb: 1 }}>Available Functions</Box>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Function</TableCell>
                                                    <TableCell>Description</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {bracesFunctions.map((f, index) => (
                                                    <TableRow key={index}>
                                                        <TableCell>
                                                            {f.key ? <code>{f.key}(value)</code> : <code>(expression)</code>}
                                                        </TableCell>
                                                        <TableCell>{f.description}</TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </Paper>
                            </Grid>

                            {/* Examples */}
                            <Grid size={12}>
                                <Paper elevation={1} sx={{ p: 2, mt: 2 }}>
                                    <Box sx={{ fontWeight: 'bold', mb: 1 }}>Examples</Box>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Example</TableCell>
                                                    <TableCell>Description</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell><code>host=example.com</code></TableCell>
                                                    <TableCell>Find URLs with hostname "example.com"</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><code>cats=news</code></TableCell>
                                                    <TableCell>Find URLs in the "news" category</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><code>host=example.com AND cats=news</code></TableCell>
                                                    <TableCell>Find "example.com" URLs in the "news" category</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><code>"social media"</code></TableCell>
                                                    <TableCell>Find URLs containing "social media" in any field</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><code>host=*.com</code></TableCell>
                                                    <TableCell>Find URLs with .com domains (using wildcard)</TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </Paper>
                            </Grid>
                        </Grid>
                    </Alert>
                </Grid>
            )}
        </>
    )
}

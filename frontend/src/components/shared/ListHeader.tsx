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
    Card,
    CardContent,
    Stack,
    Tooltip,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import DownloadIcon from "@mui/icons-material/Download"
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import InfoIcon from '@mui/icons-material/Info';
import {CSVLink} from "react-csv"

import {bracesFunctions, BuildSyntaxTree, SearchParser} from "../../searchParser";
import {formatDateForFilename} from "../../util/DateString";
import {StringKV} from "../../types/stringKV";
import {FieldDefinition} from "../../searchParser/fieldDefinition";
import {useQueryParamState} from "../../hooks/useQueryParamState";


interface ListHeaderProps {
    onCreate: () => void,
    setQuickSearch: (parser: SearchParser | null) => void,
    addElement: string,
    downloadRows:  StringKV[],
    availableFields: FieldDefinition[],
    isLocked?: boolean,
}
export const ListHeader = (props: ListHeaderProps) => {
    const {
        onCreate,
        setQuickSearch,
        addElement,
        downloadRows,
        availableFields,
        isLocked = false,
    } = props;

    const support_create = !isLocked;

    const [myTree, setMyTree] = React.useState<SearchParser | null>(null);
    const [treeError, setTreeError] = React.useState<string | null>(null);
    const [isInfoOpen, setIsInfoOpen] = React.useState<boolean>(false);

    // Keep input in sync with URL via small reusable hook
    const { value: searchStringInput, setValue: setSearchStringInput, debounced: debouncedSearchString } = useQueryParamState({ param: 'q' });

    // Parse Search Tree
    React.useEffect(() => {
        let tree: SearchParser | null = null;
        try {
            tree = BuildSyntaxTree(debouncedSearchString, availableFields);
            setTreeError(null);
        } catch(e: any) {
            setTreeError(e?.message || 'Unknown parsing error');
        }
        setMyTree(tree);
        // propagate changes to the parent component
        setQuickSearch(tree);
    }, [debouncedSearchString, setQuickSearch, availableFields]);

    return (
        <Box sx={{ m: 3 }}>
            { /* Header Box */ }
            <Card variant="outlined" sx={{ bgcolor: 'action.hover', mb: 2 }}>
                <CardContent sx={{ '&:last-child': { pb: 2 } }}>
                    <Grid container spacing={2}>
                        { /* Search Bar */ }
                        <Grid size={{ xs: 12, md: support_create ? 7 : 10 }}>
                            <TextField
                                fullWidth
                                label="Quick Search"
                                size="small"
                                variant="outlined"
                                value={searchStringInput}
                                onChange={event => setSearchStringInput(event.target.value)}
                                slotProps={{
                                    input: {
                                        endAdornment: (
                                            <InputAdornment position="end">
                                                <Tooltip title={isInfoOpen ? 'Hide Search Help' : 'Show Search Help'}>
                                                    <IconButton
                                                        onClick={() => setIsInfoOpen(!isInfoOpen)}
                                                        edge="end"
                                                        size="small"
                                                    >
                                                        {isInfoOpen ? <InfoIcon color="primary" /> : <InfoOutlinedIcon />}
                                                    </IconButton>
                                                </Tooltip>
                                            </InputAdornment>
                                        )
                                    }
                                }}
                            />
                        </Grid>
                        { /* Add-Button */ }
                        { support_create && (
                            <Grid size={{ xs: 9, md: 4 }} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={() => onCreate!()}
                                    sx={{ height: '40px', maxWidth: '300px' }}
                                >
                                    + Add {addElement}
                                </Button>
                            </Grid>
                        )}
                        { /* Download Button */ }
                        <Grid size={{ xs: 3, md: support_create ? 1 : 2 }} sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                            <Tooltip title="Download CSV">
                                <Button
                                    aria-label="download csv"
                                    color="primary"
                                    variant="outlined"
                                    component="span"
                                    sx={{ minWidth: '40px', width: '40px', height: '40px', p: 0 }}
                                >
                                    <CSVLink
                                        data={downloadRows!}
                                        separator={";"}
                                        filename={`download_${addElement.toLowerCase()}_${formatDateForFilename()}.csv`}
                                        target="_blank"
                                        style={{ textDecoration: 'none', color: 'inherit', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}
                                    >
                                        <DownloadIcon />
                                    </CSVLink>
                                </Button>
                            </Tooltip>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            { /* Search Syntax Error (if any) */ }
            { treeError && (
                <Alert severity="error" sx={{ mb: 2 }}>Invalid Search: { treeError }</Alert>
            )}

            { /* Search Syntax Guide & Examples */ }
            { isInfoOpen && (
                <Alert severity="info" sx={{ mb: 2 }}>
                    <Grid container spacing={2} sx={{ justifyContent: "center" }}>
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
                                                    <TableCell>Find URLs with hostname exact "example.com"</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><code>cats=*news*</code></TableCell>
                                                    <TableCell>Find URLs in the "news" category</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><code>host=example.com AND cats=news</code></TableCell>
                                                    <TableCell>Find "example.com" URLs in (only) the "news" category</TableCell>
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
            )}
        </Box>
    )
}

import React from 'react';
import {
    Button,
    Container,
    Divider,
    TextField,
    Typography,
    Card,
    CardContent,
    CardHeader,
    Stack,
    Box,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    CircularProgress,
    IconButton,
    Tooltip
} from "@mui/material";
import Grid from "@mui/material/Grid";
import {
    Search as SearchIcon,
    Clear as ClearIcon,
    InfoOutlined as InfoIcon,
    CheckCircleOutlined as SuccessIcon,
    ErrorOutlined as ErrorIcon,
    History as HistoryIcon,
    Download as DownloadIcon
} from "@mui/icons-material";
import { CSVLink } from "react-csv";
import {useAuth} from "../../hooks/useLogin";
import {useNotification} from "../../hooks/useNotification";
import {testApi} from "../../api/core";
import {RestTestResult} from "../../types/core";
import {CategoryChip} from "../shared/CategoryChip";

function TestPage() {
    const authMgmt = useAuth();
    const { showError } = useNotification();

    // State info for the Page
    const [results, setResults] = React.useState<RestTestResult[]>([]);
    const [value, setValue] = React.useState<string>("");
    const [submitting, setSubmitting] = React.useState<boolean>(false);

    const onSubmit = async () => {
        if (!value) return;
        
        const urls = value.split('\n').map(u => u.trim()).filter(u => u.length > 0);
        if (urls.length === 0) return;

        setSubmitting(true);
        setResults([]);

        try {
            const res = await testApi(authMgmt.token, urls);
            setResults(res);
        } catch (e: any) {
            showError(e?.message ?? "Failed to run test");
        } finally {
            setSubmitting(false);
        }
    };

    const onClear = () => {
        setValue("");
        setResults([]);
    };

    const csvData = React.useMemo(() => {
        return results.map(res => ({
            Input: res.input,
            "Matched Pattern": res.matched_url || "",
            "Local Categories": res.local_categories.map(c => c.name).join(", "),
            "Bluecoat (Live)": res.bc_categories.join(", ")
        }));
    }, [results]);

    return (
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ mb: 4 }}>
                <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
                    <HistoryIcon color="primary" sx={{ fontSize: 32 }} />
                    <Box>
                        <Typography variant="h4" sx={{ fontWeight: 700 }}>
                            URL Analysis Tool
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <InfoIcon fontSize="small" />
                            Live matching against the <strong>Production Branch</strong>
                        </Typography>
                    </Box>
                </Stack>
            </Box>

            <Grid container spacing={4}>
                {/* Left Side: Input */}
                <Grid size={{ xs: 12, lg: 4 }}>
                    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                        <CardHeader 
                            title="Input Hostnames" 
                            titleTypographyProps={{ variant: 'h6', fontWeight: 600 }}
                            action={
                                <Tooltip title="Clear Input">
                                    <IconButton onClick={onClear} disabled={!value && results.length === 0}>
                                        <ClearIcon />
                                    </IconButton>
                                </Tooltip>
                            }
                        />
                        <Divider />
                        <CardContent>
                            <TextField
                                autoFocus
                                fullWidth
                                multiline
                                rows={10}
                                variant="outlined"
                                label="One hostname per line"
                                placeholder={"example.com\ngoogle.com\ntest.org"}
                                value={value}
                                onChange={(e) => setValue(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && e.ctrlKey) {
                                        onSubmit();
                                    }
                                }}
                                sx={{
                                    '& .MuiOutlinedInput-root': {
                                        fontFamily: 'monospace',
                                        bgcolor: 'grey.50'
                                    }
                                }}
                                helperText="Pro-tip: Use Ctrl + Enter to run instantly"
                            />
                            <Button
                                fullWidth
                                variant="contained"
                                size="large"
                                disabled={!value || submitting}
                                onClick={onSubmit}
                                startIcon={submitting ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
                                sx={{ mt: 2, height: 56, borderRadius: 2, fontWeight: 600 }}
                            >
                                {submitting ? 'Analyzing...' : 'Run Analysis'}
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Right Side: Results */}
                <Grid size={{ xs: 12, lg: 8 }}>
                    {results.length === 0 && !submitting ? (
                        <Box 
                            sx={{ 
                                height: '100%', 
                                minHeight: 400,
                                display: 'flex', 
                                flexDirection: 'column',
                                justifyContent: 'center', 
                                alignItems: 'center',
                                border: '2px dashed',
                                borderColor: 'divider',
                                borderRadius: 4,
                                bgcolor: 'grey.50',
                                color: 'text.secondary',
                                textAlign: 'center',
                                p: 4
                            }}
                        >
                            <SearchIcon sx={{ fontSize: 64, mb: 2, opacity: 0.3 }} />
                            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                                No results to display
                            </Typography>
                            <Typography variant="body1">
                                Enter hostnames on the left and click "Run Analysis" to see how they are categorized.
                            </Typography>
                        </Box>
                    ) : (
                        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, height: '100%' }}>
                            <CardHeader 
                                title={`Analysis Results (${results.length})`}
                                titleTypographyProps={{ variant: 'h6', fontWeight: 600 }}
                                sx={{ bgcolor: 'grey.50' }}
                                action={
                                    <Button
                                        variant="outlined"
                                        size="small"
                                        startIcon={<DownloadIcon />}
                                        sx={{ mr: 1, mt: 0.5 }}
                                    >
                                        <CSVLink
                                            data={csvData}
                                            separator={";"}
                                            filename={`url_analysis_${new Date().toISOString().slice(0, 10)}.csv`}
                                            style={{ textDecoration: 'none', color: 'inherit' }}
                                        >
                                            Export CSV
                                        </CSVLink>
                                    </Button>
                                }
                            />
                            <Divider />
                            <TableContainer sx={{ maxHeight: 'calc(100vh - 350px)' }}>
                                <Table stickyHeader size="medium" sx={{ '& .MuiTableCell-root': { fontFamily: 'monospace' } }}>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell sx={{ fontWeight: 700, bgcolor: 'grey.50' }}>Input</TableCell>
                                            <TableCell sx={{ fontWeight: 700, bgcolor: 'grey.50' }}>Matched Pattern</TableCell>
                                            <TableCell sx={{ fontWeight: 700, bgcolor: 'grey.50' }}>Local Categories</TableCell>
                                            <TableCell sx={{ fontWeight: 700, bgcolor: 'grey.50' }}>Bluecoat (Live)</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {results.map((res, idx) => (
                                            <TableRow key={idx} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                                                <TableCell sx={{ fontFamily: 'monospace', verticalAlign: 'top' }}>
                                                    {res.input}
                                                </TableCell>
                                                <TableCell sx={{ verticalAlign: 'top' }}>
                                                    {res.matched_url ? (
                                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                            {res.matched_url.startsWith("ERROR") ? (
                                                                <>
                                                                    <ErrorIcon color="error" fontSize="small" />
                                                                    <Typography variant="body2" color="error" sx={{ fontWeight: 500 }}>
                                                                        {res.matched_url}
                                                                    </Typography>
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <SuccessIcon color="success" fontSize="small" />
                                                                    <Typography variant="body2" color="success.dark" sx={{ fontWeight: 500, fontFamily: 'monospace' }}>
                                                                        {res.matched_url}
                                                                    </Typography>
                                                                </>
                                                            )}
                                                        </Box>
                                                    ) : (
                                                        <Typography variant="body2" color="text.disabled">—</Typography>
                                                    )}
                                                </TableCell>
                                                <TableCell sx={{ verticalAlign: 'top' }}>
                                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75, maxWidth: 300 }}>
                                                        {res.local_categories && res.local_categories.length > 0 ? (
                                                            res.local_categories.map(cat => (<CategoryChip
                                                                key={cat.id}
                                                                category={cat}
                                                            />))
                                                        ) : (
                                                            <Typography variant="body2" color="text.disabled">None</Typography>
                                                        )}
                                                    </Box>
                                                </TableCell>
                                                <TableCell sx={{ verticalAlign: 'top' }}>
                                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75, maxWidth: 300 }}>
                                                        {res.bc_categories && res.bc_categories.length > 0 ? (
                                                            res.bc_categories.map(cat => (<CategoryChip
                                                                key={cat}
                                                                category={{name: cat}}
                                                            />))
                                                        ) : (
                                                            <Typography variant="body2" color="text.disabled">None</Typography>
                                                        )}
                                                    </Box>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Card>
                    )}
                </Grid>
            </Grid>
        </Container>
    );
}

export default TestPage;

import React from 'react';
import {Button, Container, Divider, Paper, TextField, Typography} from "@mui/material";
import Grid from "@mui/material/Grid2";
import {useAuth} from "../model/AuthContext";
import {runTest, TestReply} from "../api/other";
import {ICategory} from "../model/types/category";
import {IUrl} from "../model/types/url";

function TestPage() {
    const authMgmt = useAuth();

    // State info for the Page
    const [testResult, setTestResult] = React.useState<TestReply | null>(null);
    const [value, setValue] = React.useState<string>("");
    const [submitting, setSubmitting] = React.useState<boolean>(false);
    const [error, setError] = React.useState<string>("");

    const onSubmit = async () => {
        if (!value) return;
        setSubmitting(true);
        setError("");
        try {
            const res = await runTest(authMgmt.token, value);
            setTestResult(res);
        } catch (e: any) {
            setError(e?.message ?? "Failed to run test");
            setTestResult(null);
        } finally {
            setSubmitting(false);
        }
    };

    const renderCategories = (url: IUrl | null, locals: ICategory[] | null): string => {
        if (!url || !locals) return "";
        const map = new Map(locals.map(c => [c.id, c.name] as const));
        return url.categories.map(cid => map.get(cid) ?? cid).join(', ');
    };

    return (
        <Container maxWidth="md" sx={{ mt: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Grid container spacing={3} alignItems="center">
                        {/* a) Input Field */}
                        <Grid size={{xs:12, md:8}}>
                            <TextField
                                fullWidth
                                label="Hostname"
                                placeholder="example.com"
                                value={value}
                                onChange={(e) => setValue(e.target.value)}
                                onKeyDown={(e) => { if (e.key === 'Enter') onSubmit(); }}
                            />
                        </Grid>
                        {/* b) Submit Button */}
                        <Grid size={{xs:12, md:4}}>
                            <Button
                                fullWidth
                                variant="contained"
                                disabled={!value || submitting}
                                onClick={onSubmit}
                            >
                                {submitting ? 'Submitting…' : 'Submit'}
                            </Button>
                        </Grid>

                        {/* c) Delimiter */}
                        <Grid size={{xs:12}}>
                            <Divider>
                                <Typography variant="subtitle2" color="text.secondary">
                                    Results
                                </Typography>
                            </Divider>
                        </Grid>

                        {error && (
                            <Grid size={{xs:12}}>
                                <Typography color="error">{error}</Typography>
                            </Grid>
                        )}

                        {/* d) The (sanitized) URL used as Input */}
                        <Grid size={{xs:12}}>
                            <Typography variant="body2" color="text.secondary">Input</Typography>
                            <Typography>
                                {testResult?.input ?? '-'}
                            </Typography>
                        </Grid>

                        {/* e) The matched URL */}
                        <Grid size={{xs:12}}>
                            <Typography variant="body2" color="text.secondary">Matched URL</Typography>
                            <Typography variant="h6">
                                {testResult?.matched_url?.hostname ?? '-'}
                            </Typography>
                        </Grid>

                        {/* f) The Categories of the URL */}
                        <Grid size={{xs:12}}>
                            <Typography variant="body2" color="text.secondary">Categories</Typography>
                            <Typography>
                                {testResult ? (renderCategories(testResult.matched_url, testResult.local_categories) || '-') : '-'}
                            </Typography>
                        </Grid>

                        {/* g) The Bluecoat Categories */}
                        <Grid size={{xs:12}}>
                            <Typography variant="body2" color="text.secondary">Bluecoat Categories</Typography>
                            <Typography>
                                {testResult?.bc_categories?.length ? testResult.bc_categories.join(', ') : '-'}
                            </Typography>
                        </Grid>
                </Grid>
            </Paper>
        </Container>
    );
}

export default TestPage;

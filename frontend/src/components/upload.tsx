import React from 'react';
import {useNavigate} from 'react-router-dom';
import {loadExisting} from '../api/load_existing';
import {useAuth} from '../model/AuthContext';
import { 
    Button, 
    TextField, 
    Typography, 
    Box, 
    Container, 
    Paper, 
    ToggleButtonGroup, 
    ToggleButton, 
    Alert, 
    CircularProgress,
    List,
    ListItem,
    ListItemText,
    IconButton,
} from '@mui/material';
import Grid from "@mui/material/Grid2";
import UploadFileIcon from '@mui/icons-material/UploadFile';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import CloseIcon from '@mui/icons-material/Close';
import {formatDateString} from "../util/DateString";

const UploadPage = () => {
    const navigate = useNavigate();
    const { token } = useAuth();

    const [files, setFiles] = React.useState<File[]>([]);
    const [text, setText] = React.useState<string>('');
    const [isLoading, setIsLoading] = React.useState<boolean>(false);
    const [error, setError] = React.useState<string | null>(null);
    const [success, setSuccess] = React.useState<string | null>(null);
    const [uploadType, setUploadType] = React.useState<'file' | 'text'>('file');
    const [prefix, setPrefix] = React.useState<string>(`IMPORTED_${formatDateString()}_`);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            // Convert FileList to array and add new files
            const newFiles = Array.from(e.target.files);

            // Limit to 5 files total
            setFiles(prevFiles => {
                const updatedFiles = [...prevFiles, ...newFiles];
                return updatedFiles.slice(0, 5);
            });

            setError(null);
            setSuccess(null);
        }
    };

    const handleRemoveFile = (index: number) => {
        setFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
        setSuccess(null);
    };

    const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setText(e.target.value);
        setError(null);
        setSuccess(null);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setSuccess(null);

        try {
            if (!token) {
                throw new Error('You must be logged in to upload');
            }

            if (uploadType === 'file' && files.length > 0) {
                // If it's an array of files, read each one and concatenate with 2 newlines
                const fileContents = await Promise.all(
                    files.map(file => file.text())
                );
                // send the array of files
                await loadExisting(token, fileContents.join('\n\n'), prefix);
            } else if (uploadType === 'text' && text.trim()) {
                await loadExisting(token, text, prefix);
            } else {
                throw new Error('Please provide a file or text to upload');
            }

            // Show success message and reset form
            setSuccess('URLs uploaded successfully!');
            setFiles([]);
            setText('');
            setPrefix(`IMPORTED_${formatDateString()}_`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxWidth="md" sx={{ mt: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom align="center">
                    Upload URLs
                </Typography>

                <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
                    <ToggleButtonGroup
                        value={uploadType}
                        exclusive
                        onChange={(_e, newValue) => {
                            if (newValue !== null) {
                                setUploadType(newValue);
                                setSuccess(null);
                            }
                        }}
                        aria-label="upload type"
                    >
                        <ToggleButton value="file" aria-label="upload file">
                            <UploadFileIcon sx={{ mr: 1 }} />
                            Upload File
                        </ToggleButton>
                        <ToggleButton value="text" aria-label="enter text">
                            <TextFieldsIcon sx={{ mr: 1 }} />
                            Enter Text
                        </ToggleButton>
                    </ToggleButtonGroup>
                </Box>

                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                    <Grid container spacing={3}>
                        <Grid size={12}>
                            <TextField
                                fullWidth
                                label="Category Prefix"
                                value={prefix}
                                onChange={(e) => {
                                    setPrefix(e.target.value);
                                    setSuccess(null);
                                }}
                                helperText="This prefix will be prepended to all categories read from the file"
                                margin="normal"
                            />
                        </Grid>

                        <Grid size={12}>
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 2 }}>
                                The Parser accepts to formats: The first option is a simple newline separated list of URLs. The second option is the default bluecoat category format, starting with "define category &lt;name&gt;" followed by the URLs and ending with "end"
                            </Typography>
                        </Grid>

                        {uploadType === 'file' ? (
                            <>
                                <Grid size={12}>
                                    <Button
                                        variant="contained"
                                        component="label"
                                        startIcon={<UploadFileIcon />}
                                        disabled={isLoading}
                                        fullWidth
                                        sx={{ py: 1.5 }}
                                    >
                                        Select a file
                                        <input
                                            type="file"
                                            hidden
                                            onChange={handleFileChange}
                                            multiple
                                        />
                                    </Button>
                                </Grid>

                                {files.length > 0 && (
                                    <Grid size={12}>
                                        <List>
                                            {files.map((file, index) => (
                                                <ListItem 
                                                    key={index}
                                                    secondaryAction={
                                                        <IconButton 
                                                            edge="end" 
                                                            aria-label="delete"
                                                            onClick={() => handleRemoveFile(index)}
                                                        >
                                                            <CloseIcon />
                                                        </IconButton>
                                                    }
                                                >
                                                    <ListItemText 
                                                        primary={file.name} 
                                                        secondary={`${(file.size / 1024).toFixed(2)} KB`} 
                                                    />
                                                </ListItem>
                                            ))}
                                        </List>
                                    </Grid>
                                )}
                            </>
                        ) : (
                            <Grid size={12}>
                                <TextField
                                    fullWidth
                                    label="Enter URLs (one per line)"
                                    multiline
                                    rows={15}
                                    value={text}
                                    onChange={handleTextChange}
                                    disabled={isLoading}
                                    placeholder="Enter URLs here, one per line"
                                    variant="outlined"
                                    sx={{ '& .MuiInputBase-root': { minHeight: '300px' } }}
                                />
                            </Grid>
                        )}

                        {error && (
                            <Grid size={12}>
                                <Alert severity="error">{error}</Alert>
                            </Grid>
                        )}

                        {success && (
                            <Grid size={12}>
                                <Alert severity="success">{success}</Alert>
                            </Grid>
                        )}

                        <Grid size={12}>
                            <Button
                                variant="contained"
                                color="primary"
                                type="submit"
                                disabled={isLoading || (uploadType === 'file' && files.length === 0) || (uploadType === 'text' && !text.trim())}
                                startIcon={isLoading ? <CircularProgress size={20} /> : null}
                                sx={{ minWidth: '120px' }}
                            >
                                {isLoading ? 'Uploading...' : 'Upload'}
                            </Button>
                            <Button
                                variant="outlined"
                                onClick={() => navigate('/')}
                                disabled={isLoading}
                            >
                                Cancel
                            </Button>
                        </Grid>
                    </Grid>
                </Box>
            </Paper>
        </Container>
    );
};

export default UploadPage;

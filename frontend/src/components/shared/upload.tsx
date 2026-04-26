import React from 'react';
import {useNavigate} from 'react-router-dom';
import {
    Button,
    TextField,
    Typography,
    Box,
    Container,
    Paper,
    ToggleButtonGroup,
    ToggleButton,
    CircularProgress,
    List,
    ListItem,
    ListItemText,
    IconButton,
    Grid,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import CloseIcon from '@mui/icons-material/Close';
import {formatDateString} from "../../util/DateString";
import {loadExisting} from "../../api/branch";
import {useAuth} from "../../hooks/useLogin";
import {useNotification} from "../../hooks/useNotification";
import {useBranch} from "../../hooks/useBranch";


const UploadPage = () => {
    const navigate = useNavigate();
    const { token } = useAuth();
    const { showError, showSuccess } = useNotification();
    const { isLocked } = useBranch();

    const [files, setFiles] = React.useState<File[]>([]);
    const [text, setText] = React.useState<string>('');
    const [isLoading, setIsLoading] = React.useState<boolean>(false);
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
        }
    };

    const handleRemoveFile = (index: number) => {
        setFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
    };

    const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setText(e.target.value);
    };


    const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
        e.preventDefault();

        // Track state
        if (isLocked) return;
        setIsLoading(true);

        try {
            let content = '';
            if (uploadType === 'file' && files.length > 0) {
                // If it's an array of files we simply read all of them and join them with newlines
                const fileContents = await Promise.all(files.map(file => file.text()));
                content = fileContents.join('\n\n');
            } else if (uploadType === 'text' && text.trim()) {
                content = text;
            } else {
                throw new Error('Please provide a file or text to upload');
            }

            await loadExisting(token, content, prefix);
            showSuccess("Database uploaded successfully");

            // Reset form
            setFiles([]);
            setText('');
            setPrefix(`IMPORTED_${formatDateString()}_`);
        } catch (err: any) {
            showError(err.message || "Failed to upload database");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxWidth="md" sx={{ mt: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom align="center">
                    Upload LocalDB
                </Typography>

                <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
                    <ToggleButtonGroup
                        value={uploadType}
                        exclusive
                        onChange={(_e, newValue) => {
                            if (newValue !== null) {
                                setUploadType(newValue);
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
                                }}
                                helperText="This prefix will be prepended to all categories read from the file"
                                margin="normal"
                            />
                        </Grid>

                        <Grid size={12}>
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 2 }}>
                                The Parser accepts the default bluecoat category format, starting with "define category &lt;name&gt;" followed by the URLs and ending with "end"
                            </Typography>
                        </Grid>

                        {uploadType === 'file' ? (
                            <>
                                <Grid size={12}>
                                    <Button
                                        variant="contained"
                                        component="label"
                                        startIcon={<UploadFileIcon />}
                                        disabled={isLoading || isLocked}
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
                                    disabled={isLoading || isLocked}
                                    placeholder="Enter URLs here, one per line"
                                    variant="outlined"
                                    sx={{ '& .MuiInputBase-root': { minHeight: '300px' } }}
                                />
                            </Grid>
                        )}

                        <Grid size={12}>
                            <Button
                                variant="contained"
                                color="primary"
                                type="submit"
                                disabled={isLoading || isLocked || (uploadType === 'file' && files.length === 0) || (uploadType === 'text' && !text.trim())}
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

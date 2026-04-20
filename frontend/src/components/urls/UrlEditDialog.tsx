import React from 'react';
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Stack,
    TextField,
} from "@mui/material";
import { IRestURLDetail } from "../../types/url";
import { TriState } from "../../types/EditDialogState";
import { simpleStringCheck } from "../../util/InputValidators";

export interface UrlEditDialogProps {
    urlDetail: TriState<IRestURLDetail>,
    onClose: () => void,
    onSave: (id: string | null, url: string, description: string) => void,
}

export const UrlEditDialog = (props: UrlEditDialogProps) => {
    const { urlDetail, onClose, onSave } = props;

    const [url, setUrl] = React.useState('');
    const [description, setDescription] = React.useState('');

    // validate inputs
    const urlError: string|null = React.useMemo(
        () => simpleStringCheck(url),
        [url],
    );

    React.useEffect(() => {
        if (!urlDetail.isNull()) {
            setUrl(urlDetail.getValue()!.url.url);
            setDescription(urlDetail.getValue()!.url.description);
        } else {
            setUrl("");
            setDescription("");
        }
    }, [urlDetail]);

    const handleSave = () => {
        if (urlError != null) {
            // only continue if the inputs are valid
            return;
        }
        onSave(urlDetail.isNull() ? null : urlDetail.getValue()!.url.id, url, description);
    };

    return (
        <Dialog open={!urlDetail.isClosed()} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>{urlDetail.isNull() ? "Create New URL" : "Edit URL"}</DialogTitle>
            <DialogContent>
                <Stack spacing={2} sx={{ mt: 1 }}>
                    <TextField
                        autoFocus
                        label="URL"
                        fullWidth
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        error={urlError != null}
                        helperText={urlError}
                    />
                    <TextField
                        label="Description"
                        fullWidth
                        multiline
                        rows={2}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                    />
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button 
                    onClick={handleSave} 
                    variant="contained" 
                    disabled={urlError != null}
                >
                    Save
                </Button>
            </DialogActions>
        </Dialog>
    );
};

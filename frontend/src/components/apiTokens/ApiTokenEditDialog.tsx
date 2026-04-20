import React from 'react';
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Stack,
    TextField,
} from '@mui/material';
import { IApiToken } from '../../types/apiToken';
import { TriState } from "../../types/EditDialogState";
import { simpleStringCheck } from "../../util/InputValidators";

export interface ApiTokenEditDialogProps {
    tokenDetail: TriState<IApiToken>,
    onClose: () => void,
    onSave: (id: string | null, description: string) => void,
}

export const ApiTokenEditDialog = (props: ApiTokenEditDialogProps) => {
    const { tokenDetail, onClose, onSave } = props;

    const [description, setDescription] = React.useState('');

    const descriptionError: string|null = React.useMemo(
        () => simpleStringCheck(description),
        [description],
    );

    React.useEffect(() => {
        if (!tokenDetail.isNull()) {
            setDescription(tokenDetail.getValue()!.description);
        } else {
            setDescription("");
        }
    }, [tokenDetail]);

    const handleSave = () => {
        if (descriptionError != null) return;
        onSave(tokenDetail.isNull() ? null : tokenDetail.getValue()!.id, description);
    };

    return (
        <Dialog open={!tokenDetail.isClosed()} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>{tokenDetail.isNull() ? "Create New API Token" : "Edit API Token"}</DialogTitle>
            <DialogContent>
                <Stack spacing={2} sx={{ mt: 1 }}>
                    <TextField
                        autoFocus
                        label="Description"
                        fullWidth
                        multiline
                        rows={2}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        error={descriptionError != null}
                        helperText={descriptionError}
                    />
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button 
                    onClick={handleSave} 
                    variant="contained" 
                    disabled={descriptionError != null}
                >
                    Save
                </Button>
            </DialogActions>
        </Dialog>
    );
};

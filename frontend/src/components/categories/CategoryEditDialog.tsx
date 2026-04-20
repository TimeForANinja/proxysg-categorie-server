import React from 'react';
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Stack,
    TextField, Tooltip, Typography,
} from "@mui/material";
import { ICategory } from "../../types/category";
import { TriState } from "../../types/EditDialogState";
import { simpleNameCheck } from "../../util/InputValidators";
import {colorLUT, hexToColor} from "../../util/colormixer";

export interface CategoryEditDialogProps {
    categoryDetail: TriState<ICategory>,
    onClose: () => void,
    onSave: (id: string | null, name: string, description: string, color: number) => void,
}

export const CategoryEditDialog = (props: CategoryEditDialogProps) => {
    const { categoryDetail, onClose, onSave } = props;

    const [name, setName] = React.useState('');
    const [description, setDescription] = React.useState('');
    const [color, setColor] = React.useState<number>(hexToColor(colorLUT[1].fg));

    const nameError: string|null = React.useMemo(
        () => simpleNameCheck(name),
        [name],
    );

    React.useEffect(() => {
        if (!categoryDetail.isNull()) {
            setName(categoryDetail.getValue()!.name);
            setDescription(categoryDetail.getValue()!.description);
            setColor(categoryDetail.getValue()!.color);
        } else {
            setName("");
            setDescription("");
            setColor(hexToColor(colorLUT[1].fg));
        }
    }, [categoryDetail]);

    const handleSave = () => {
        if (nameError != null) return;
        onSave(categoryDetail.isNull() ? null : categoryDetail.getValue()!.id, name, description, color);
    };

    return (
        <Dialog open={!categoryDetail.isClosed()} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>{categoryDetail.isNull() ? "Create New Category" : "Edit Category"}</DialogTitle>
            <DialogContent>
                <Stack spacing={2} sx={{ mt: 1 }}>
                    <TextField
                        autoFocus
                        label="Name"
                        fullWidth
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        error={nameError != null}
                        helperText={nameError}
                    />
                    <TextField
                        label="Description"
                        fullWidth
                        multiline
                        rows={2}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                    />
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <Typography variant="caption" color="text.secondary">Quick Color Selection</Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                            {Object.entries(colorLUT).map(([id, profile]) => (
                                <Tooltip key={id} title={profile.name}>
                                    <Box
                                        onClick={() => setColor(hexToColor(profile.fg))}
                                        sx={{
                                            width: 32,
                                            height: 32,
                                            bgcolor: profile.fg,
                                            borderRadius: color === hexToColor(profile.fg) ? '0%' : '50%',
                                            border: color === hexToColor(profile.fg) ? '3px solid' : 'none',
                                            outline: '2px solid black',
                                            borderColor: profile.bg,
                                            cursor: 'pointer',
                                            '&:hover': {
                                                opacity: 0.8,
                                                transform: 'scale(1.1)'
                                            },
                                            transition: 'transform 0.1s'
                                        }}
                                    />
                                </Tooltip>
                            ))}
                        </Box>
                    </Box>
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button 
                    onClick={handleSave} 
                    variant="contained" 
                    disabled={nameError != null}
                >
                    Save
                </Button>
            </DialogActions>
        </Dialog>
    );
};

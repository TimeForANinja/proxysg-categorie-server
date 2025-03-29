import React from "react";
import {
    Button,

    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle
} from "@mui/material";

interface ConfirmDeletionDialogProps {
    onConfirmation: (del: boolean) => void,
    header: string,
    body: string,
    isOpen: boolean,
}
export function ConfirmDeletionDialog(props: ConfirmDeletionDialogProps) {
    const {
        onConfirmation,
        header,
        body,
        isOpen,
    } = props;

    return (
        <Dialog
            open={isOpen}
            onClose={() => onConfirmation(false)}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >
            <DialogTitle id="alert-dialog-title">
                {header}
            </DialogTitle>
            <DialogContent>
                <DialogContentText id="alert-dialog-description">
                    {body}
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button onClick={() => onConfirmation(false)}>Disagree</Button>
                <Button onClick={() => onConfirmation(true)} autoFocus>
                    Agree
                </Button>
            </DialogActions>
        </Dialog>
    )
}
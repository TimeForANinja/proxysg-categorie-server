import React from "react";
import {
    Box,
    TextField,
    Button,
} from "@mui/material";
import Grid from "@mui/material/Grid2";

interface ListHeaderProps {
    onCreate: () => void,
    setQuickSearch: (search: string) => void,
    addElement: string
}
export const ListHeader = (props: ListHeaderProps) => {
    const {
        onCreate,
        setQuickSearch,
        addElement,
    } = props;

    return (
        <>
            <Grid size={8}>
                <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                    <TextField
                        margin="dense"
                        label="Quick Search"
                        size="small"
                        variant="filled"
                        onChange={event => setQuickSearch(event.target.value)}
                    />
                </Box>
            </Grid>
            <Grid size={4}>
                <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                    <Button
                        variant="outlined"
                        onClick={() => onCreate()}
                    >
                        + Add {addElement}
                    </Button>
                </Box>
            </Grid>
        </>
    )
}

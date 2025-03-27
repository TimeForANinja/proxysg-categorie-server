import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

import React from "react";

export const ListHeader = (props: {
    handleEditOpen: (param: null) => void,
    setQuickSearch: (search: string) => void,
}) => {
    const {
        handleEditOpen,
        setQuickSearch
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
                        onClick={() => handleEditOpen(null)}
                    >
                        + Add Category
                    </Button>
                </Box>
            </Grid>
        </>
    )
}
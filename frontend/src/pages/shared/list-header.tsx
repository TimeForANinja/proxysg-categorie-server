import React from "react";
import {
    Box,
    TextField,
    Button,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import DownloadIcon from "@mui/icons-material/Download"
import { CSVLink } from "react-csv"

// Utility method to calculate a Date-Time-Stamp to include in filenames
const formatDateForFilename = (): string => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed, so add 1
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;
}

interface ListHeaderProps {
    onCreate: () => void,
    setQuickSearch: (search: string) => void,
    addElement: string,
    downloadRows:  {[key: string]: string}[] | null,
}
export const ListHeader = (props: ListHeaderProps) => {
    const {
        onCreate,
        setQuickSearch,
        addElement,
        downloadRows,
    } = props;

    const hasDownload = downloadRows != null && downloadRows.length > 0;

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
            <Grid size={hasDownload ? 3 : 4}>
                <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                    <Button
                        variant="outlined"
                        onClick={() => onCreate()}
                    >
                        + Add {addElement}
                    </Button>
                </Box>
            </Grid>
            { hasDownload && (
                <Grid size={1}>
                    <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                        <Button
                            aria-label="delete"
                            color="primary"
                            variant="outlined"
                        >
                            <CSVLink
                                data={downloadRows!}
                                separator={";"}
                                filename={`download_${formatDateForFilename()}.csv`}
                                target="_blank"
                            >
                                <DownloadIcon />
                            </CSVLink>
                        </Button>
                    </Box>
                </Grid>
            )}
        </>
    )
}

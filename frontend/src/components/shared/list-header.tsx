import React from "react";
import {
    Box,
    TextField,
    Button,
    Alert,
    InputAdornment,
    IconButton,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import DownloadIcon from "@mui/icons-material/Download"
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import InfoIcon from '@mui/icons-material/Info';
import {CSVLink} from "react-csv"

import {BuildSyntaxTree, SearchParser} from "../../searchParser";

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
    setQuickSearch: (parser: SearchParser | null) => void,
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

    const [myTree, setMyTree] = React.useState<SearchParser | null>(null);
    const [treeError, setTreeError] = React.useState<string | null>(null);
    const [isInfoOpen, setIsInfoOpen] = React.useState<boolean>(false);

    const updateSearch = (newStr: string) => {
        let tree: SearchParser | null = null;
        try {
            tree = BuildSyntaxTree(newStr);
            setTreeError(null);
            console.log("Search Query:", tree.print());
        } catch(e: Error | any) {
            setTreeError(e?.message);
            console.log("Invalid Error:", e?.message, e?.stack);
        }
        setMyTree(tree);
        setQuickSearch(tree);
    }

    return (
        <>
            <Grid size={8}>
                <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                    <TextField
                        margin="dense"
                        label="Quick Search"
                        size="small"
                        variant="filled"
                        onChange={event => updateSearch(event.target.value)}
                        slotProps={{
                            input: {
                                endAdornment: <InputAdornment position="end">
                                    <IconButton
                                        aria-label={isInfoOpen ? 'hide Info' : 'display Info'}
                                        onClick={() => setIsInfoOpen(!isInfoOpen)}
                                        edge="end"
                                    >
                                        {isInfoOpen ? <InfoIcon/> : <InfoOutlinedIcon/>}
                                    </IconButton>
                                </InputAdornment>
                            }
                        }}
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
            { treeError && (
                <Grid size={12}>
                    <Alert severity="error">Invalid Search: { treeError }</Alert>
                </Grid>
            )}
            { isInfoOpen && (
                <Grid size={12}>
                    <Alert
                        severity="info"
                    >
                        <Grid
                            container
                            spacing={1}
                            justifyContent="center"
                            alignItems="center"
                            sx={{ alignItems: "flex-start" }}
                        >
                            <Grid size={12}>
                                { myTree?.print() }
                            </Grid>
                            { /* TODO: show known functions, operators, fields */ }
                        </Grid>
                    </Alert>
                </Grid>
            )}
        </>
    )
}

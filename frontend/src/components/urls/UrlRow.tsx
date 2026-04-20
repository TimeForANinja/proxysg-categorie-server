import React from 'react';
import {
    Box,
    Collapse,
    IconButton,
    Paper,
    Stack,
    TableCell,
    TableRow,
    Typography,
    Tabs,
    Tab,
} from "@mui/material";
import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import TimelineOppositeContent from '@mui/lab/TimelineOppositeContent';
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import HistoryIcon from '@mui/icons-material/History';
import CategoryIcon from '@mui/icons-material/Category';
import TimelineIcon from '@mui/icons-material/Timeline';

import { getHistory } from "../../api/history";
import { IRestURLDetail } from "../../types/url";
import { IRestCommit } from "../../types/history";
import { ICategory } from "../../types/category";
import { LUT } from "../../types/LookUpTable";
import {CategoryChipList} from "../shared/CategoryChip";
import { UrlCategoryMappings } from "../shared/UrlCategoryMappings";
import {formatUnixTimestamp } from "../../util/DateString";
import { useAuth } from "../../hooks/useLogin";
import {short_uuid} from "../../util/uuid";

export interface UrlRowProps {
    urlDetail: IRestURLDetail,
    branch: string,
    isLocked: boolean,
    onEdit: (url: IRestURLDetail) => void,
    onDelete: (url: IRestURLDetail) => void,
    categories: LUT<ICategory>,
    onRefresh: () => void,
}

export const UrlRow = React.memo(function UrlRow(props: UrlRowProps) {
    const { urlDetail, branch, isLocked, onEdit, onDelete, categories, onRefresh } = props;
    const authMgmt = useAuth();

    const [open, setOpen] = React.useState(false);
    const [history, setHistory] = React.useState<IRestCommit[]>([]);
    const [tabValue, setTabValue] = React.useState(0);

    const toggleOpen = () => {
        if (!open && history.length === 0) {
            getHistory(authMgmt.token, branch, [urlDetail.url.id])
                .then(setHistory)
                .catch(err => console.error('Failed to load history:', err));
        }
        setOpen(prev => !prev);
    };

    const renderExperimentalContent = () => {
        const mappings = (
            <UrlCategoryMappings
                urlDetail={urlDetail}
                isLocked={isLocked}
                categories={categories}
                onRefresh={onRefresh}
            />
        );

        const timeline = (
            <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TimelineIcon fontSize="small" /> Activity Timeline
                </Typography>
                {history.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                        No history available for this URL.
                    </Typography>
                ) : (
                    <Timeline position="right" sx={{ p: 0, m: 0 }}>
                        {history.map((commit, i) => (
                            <TimelineItem key={commit.uuid}>
                                <TimelineOppositeContent sx={{ py: '12px', px: 2, flex: 0.15, minWidth: 120 }}>
                                    <Typography variant="caption" color="text.secondary">
                                        {formatUnixTimestamp(commit.created_at)}
                                    </Typography>
                                </TimelineOppositeContent>
                                <TimelineSeparator>
                                    <TimelineDot color="primary" variant="outlined" />
                                    {i < history.length - 1 && <TimelineConnector />}
                                </TimelineSeparator>
                                <TimelineContent sx={{ py: '12px', px: 2 }}>
                                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                        {commit.author}
                                    </Typography>
                                    <Typography variant="body2">{commit.description}</Typography>
                                </TimelineContent>
                            </TimelineItem>
                        ))}
                    </Timeline>
                )}
            </Box>
        );

        return (
            <Paper variant="outlined" sx={{ width: '100%', mb: 1 }}>
                <Tabs
                    value={tabValue}
                    onChange={(_, v) => setTabValue(v)}
                    sx={{ borderBottom: 1, borderColor: 'divider', px: 2, bgcolor: 'grey.50' }}
                >
                    <Tab icon={<CategoryIcon />} label="Mappings" iconPosition="start" />
                    <Tab icon={<HistoryIcon />} label="History" iconPosition="start" />
                </Tabs>
                <Box sx={{ minHeight: 200 }}>
                    {tabValue === 0 ? mappings : timeline}
                </Box>
            </Paper>
        );
    };

    return (
        <React.Fragment>
            <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={toggleOpen}
                    >
                        {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{short_uuid(urlDetail.url.id)}</TableCell>
                <TableCell>{urlDetail.url.url}</TableCell>
                <TableCell>{urlDetail.url.description}</TableCell>
                <TableCell>
                    <Stack component="div" direction="row" spacing={0.5} sx={{ flexWrap: "wrap" }}>
                        <CategoryChipList categories={urlDetail.categories.map(c => c.category)} />
                    </Stack>
                </TableCell>
                <TableCell align="right">
                    {!isLocked && (
                        <>
                            <IconButton aria-label="edit url" onClick={() => onEdit(urlDetail)} size="small">
                                <EditIcon />
                            </IconButton>
                            <IconButton aria-label="delete url" onClick={() => onDelete(urlDetail)} size="small">
                                <DeleteIcon />
                            </IconButton>
                        </>
                    )}
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0, paddingRight: 0 }} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ 
                            ml: 2, 
                            mr: 0, 
                            mb: 2, 
                            mt: 1, 
                            borderLeft: '4px solid', 
                            borderColor: 'primary.main',
                            pl: 2
                        }}>
                            {renderExperimentalContent()}
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    )
});

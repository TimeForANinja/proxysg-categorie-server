import React from 'react';
import Select, {StylesConfig} from 'react-select';
import chroma from 'chroma-js';

import {getCategories, ICategory} from "../api/categories";
import {getURLs, IURL} from "../api/urls";
import {colors} from "../api/colormixer";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import IconButton from "@mui/material/IconButton";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import Paper from '@mui/material/Paper';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Collapse from '@mui/material/Collapse';


type ColorOPT = {
    value: number,
    label: string,
    color: string,
}

const mapCategoryToSelectProps = (category: ICategory): ColorOPT => ({
    value: category.id,
    label: category.name,
    color: colors[category.color]
});


function BuildRow(props: { url: IURL, categories: ICategory[]}) {
    const { url, categories } = props;
    const [isOpen, setIsOpen] = React.useState(false);

    return (
        <React.Fragment>
            <TableRow key={url.id}>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell>{url.id}</TableCell>
                <TableCell>{url.hostname}</TableCell>
                <TableCell>
                    <Select
                        defaultValue={categories.filter(category => url.categories.includes(category.id)).map(mapCategoryToSelectProps)}
                        isMulti
                        options={categories.map(mapCategoryToSelectProps)}
                        styles={colourStyles}
                    />
                </TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0}} colSpan={4}>
                    <Collapse in={isOpen} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1}} >
                            <Typography variant="h6" gutterBottom component="div">
                                History
                            </Typography>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
            </React.Fragment>
    )
}


function MatchingListPage() {
    const [urls, setURLs] = React.useState<IURL[]>([]);
    const [categories, setCategory] = React.useState<ICategory[]>([]);

    React.useEffect(() => {
        Promise.all([getURLs(), getCategories()])
            .then(([urlsData, categoriesData]) => {
                setURLs(urlsData);
                setCategory(categoriesData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    return (
        <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
            <TableHead>
            <TableRow>
                <TableCell />
                <TableCell>ID</TableCell>
                <TableCell>Hostname</TableCell>
                <TableCell>Categories</TableCell>
            </TableRow>
            </TableHead>
            <TableBody>
            {urls.map(url =>
                <BuildRow key={url.id} url={url} categories={categories}></BuildRow>
            )}
            </TableBody>
        </Table>
        </TableContainer>
    );
}

const colourStyles: StylesConfig<ColorOPT, true> = {
    control: (styles) => ({ ...styles, backgroundColor: 'white' }),
    option: (styles, { data, isDisabled, isFocused, isSelected }) => {
        const color = chroma(data.color);
        return {
            ...styles,
            backgroundColor: isDisabled
                ? undefined
                : isSelected
                    ? data.color
                    : isFocused
                        ? color.alpha(0.1).css()
                        : undefined,
            color: isDisabled
                ? '#ccc'
                : isSelected
                    ? chroma.contrast(color, 'white') > 2
                        ? 'white'
                        : 'black'
                    : data.color,
            cursor: isDisabled ? 'not-allowed' : 'default',

            ':active': {
                ...styles[':active'],
                backgroundColor: !isDisabled
                    ? isSelected
                        ? data.color
                        : color.alpha(0.3).css()
                    : undefined,
            },
        };
    },
    multiValue: (styles, { data }) => {
        const color = chroma(data.color);
        return {
            ...styles,
            backgroundColor: color.alpha(0.1).css(),
        };
    },
    multiValueLabel: (styles, { data }) => ({
        ...styles,
        color: data.color,
    }),
    multiValueRemove: (styles, { data }) => ({
        ...styles,
        color: data.color,
        ':hover': {
            backgroundColor: data.color,
            color: 'white',
        },
    }),
};

export default MatchingListPage;

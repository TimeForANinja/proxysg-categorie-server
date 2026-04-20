import React from "react";
import {Autocomplete, Box, TextField} from "@mui/material";

import {getLUTValues, LUT} from "../../types/LookUpTable";
import {ICategory} from "../../types/category";
import {CompareLists} from "../../util/ArrayDiff";
import {CategoryChipList} from "./CategoryChip";
import {colorToHex} from "../../util/colormixer";

interface CategoryPickerProps {
    isCategories: ICategory[],
    onChange: (newCats: string[], added: string[], removed: string[]) => void,
    categories: LUT<ICategory>,
    disabled?: boolean,
}
export function CategoryPicker(props: CategoryPickerProps) {
    const {
        isCategories,
        onChange,
        categories,
        disabled = false,
    } = props;

    // helper function, triggered when the category selector changes
    const handleChange = (_event: React.SyntheticEvent, new_cats: ICategory[]) => {
        const currentIds = isCategories.map(c => c.id);
        const newIds = new_cats.map(c => c.id);
        const { added, removed } = CompareLists(currentIds, newIds);
        onChange(newIds, added, removed);
    };

    const categoryOptions = React.useMemo(() => getLUTValues(categories), [categories]);

    return (
        <Autocomplete
            multiple
            disableCloseOnSelect
            size="small"
            options={categoryOptions}
            getOptionLabel={(cat) => cat.name}
            value={isCategories}
            onChange={handleChange}
            disabled={disabled}
            isOptionEqualToValue={(a, b) => a.id === b.id}
            renderValue={(values, getItemProps) => (
                <CategoryChipList categories={values} getItemProps={getItemProps}/>
            )}
            renderOption={(props, option) => {
                // renderOption renders the items shown in the dropdown menu
                const { key, ...optionProps } = props;
                const colorHex = colorToHex(option.color);
                return (
                    <li key={key} {...optionProps}>
                        <Box
                            sx={{
                                width: 16,
                                height: 16,
                                borderRadius: '50%',
                                bgcolor: colorHex,
                                mr: 1,
                                border: '1px solid grey'
                            }}
                        />
                        <Box
                            sx={{
                                flexGrow: 1,
                                '& span': {
                                    color: 'text.secondary',
                                },
                            }}
                        >
                            {option.name}
                        </Box>
                    </li>
                );
            }}
            renderInput={(params) => (
                <TextField
                    {...params}
                    variant="standard"
                    placeholder="Categories"
                />
            )}
        />
    );
}

import React from "react";
import {Autocomplete, Box, Chip, TextField} from "@mui/material";

import {getLUTValues, LUT} from "../../types/LookUpTable";
import {ICategory} from "../../types/category";
import {CompareLists} from "../../util/ArrayDiff";

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
            renderValue={(values, getItemProps) =>
                values.map((val, index: number) => {
                    const { key, ...tagProps } = getItemProps({ index });
                    return (
                        <Chip
                            variant="outlined"
                            label={val.name}
                            key={key}
                            {...tagProps}
                        />
                    );
                })
            }
            renderOption={(props, option) => {
                const { key, ...optionProps } = props;
                return (
                    <li key={key} {...optionProps}>
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

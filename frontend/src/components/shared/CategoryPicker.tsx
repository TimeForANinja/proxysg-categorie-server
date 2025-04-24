import React from "react";
import {Autocomplete, Box, Chip, TextField} from "@mui/material";

import {getLUTValues, LUT} from "../../model/types/LookUpTable";
import {ICategory} from "../../model/types/category";
import {colorLUT} from "../../util/colormixer";
import {CompareLists} from "../../util/ArrayDiff";

interface CategoryPickerProps {
    isCategories: string[],
    onChange: (newCats: string[], added: string[], removed: string[]) => void,
    categories: LUT<ICategory>,
}
export function CategoryPicker(props: CategoryPickerProps) {
    const {
        isCategories,
        onChange,
        categories,
    } = props;

    // Create the current value for the controller `Autocomplete` component
    const selectedCategories = React.useMemo(() => {
        return isCategories.map(c => categories[c]).filter(Boolean);
    }, [isCategories, categories]);


    // helper function, triggered when the category selector changes
    const handleChange = (event: React.SyntheticEvent, new_cats: ICategory[]) => {
        if (Array.isArray(new_cats)) {
            const { added, removed } = CompareLists(isCategories, new_cats.map(c => c.id));
            onChange(new_cats.map(c => c.id), added, removed);
        }
    };

    return (
        <Autocomplete
            multiple
            disableCloseOnSelect
            size="small"
            options={getLUTValues(categories)}
            getOptionLabel={(cat) => cat.name}
            value={selectedCategories}
            onChange={handleChange}
            renderTags={(values, getTagProps) =>
                values.map((val, index: number) => {
                    const { key, ...tagProps } = getTagProps({ index });
                    return (
                        <Chip
                            variant="outlined"
                            label={val.name}
                            key={key}
                            {...tagProps}
                            sx={{
                                bgcolor: colorLUT[val.color].bg,
                                color: colorLUT[val.color].fg,
                            }}
                        />
                    );
                })
            }
            isOptionEqualToValue={(a, b) => a.id === b.id}
            renderOption={(props, option, { selected }) => {
                const { key, ...optionProps } = props;
                return (
                    <li key={key} {...optionProps}>
                        <Box
                            component="span"
                            sx={{
                                width: 14,
                                height: 14,
                                flexShrink: 0,
                                borderRadius: '3px',
                                mr: 1,
                                mt: '2px',
                            }}
                            style={{
                                backgroundColor: colorLUT[option.color].bg,
                                color: colorLUT[option.color].fg,
                            }}
                        />
                        <Box
                            sx={(t) => ({
                                flexGrow: 1,
                                '& span': {
                                    color: '#8b949e',
                                    ...t.applyStyles('light', {
                                        color: '#586069',
                                    }),
                                },
                            })}
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

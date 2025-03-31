import React from "react";
import {Autocomplete, Box, Chip, TextField} from "@mui/material";

import {getLUTValues, LUT} from "../../util/LookUpTable";
import {ICategory} from "../../api/categories";
import {colors} from "../../util/colormixer";
import {CompareLists} from "../../util/ArrayDiff";

interface CategoryPickerProps {
    isCategories: number[],
    onChange: (newCats: number[], added: number[], removed: number[]) => void,
    categories: LUT<ICategory>,
}
export function CategoryPicker(props: CategoryPickerProps) {
    const {
        isCategories,
        onChange,
        categories,
    } = props;

    // helper function, triggered when category selector changes
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
            defaultValue={isCategories.map(c => categories[c])}
            onChange={handleChange}
            renderTags={(values, getTagProps) =>
                values.map((val, index: number) => {
                    const { key, ...tagProps } = getTagProps({ index });
                    return (
                        <Chip variant="outlined" label={val.name} key={key} {...tagProps} sx={{ bgcolor: colors[val.color]}} />
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
                            style={{ backgroundColor: colors[option.color] }}
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

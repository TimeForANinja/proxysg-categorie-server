import React from "react";
import {MenuItem, Select} from "@mui/material";

import {getLUTValues, LUT} from "../../util/LookUpTable";
import {ICategory} from "../../api/categories";
import {SelectChangeEvent} from "@mui/material/Select";
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
        categories
    } = props;

    const handleChange = (event: SelectChangeEvent<number[]>) => {
        if (Array.isArray(event.target.value)) {
            const { added, removed } = CompareLists(isCategories, event.target.value);

            onChange(event.target.value, added, removed);
        }
    };

    return (
        <Select
            multiple
            value={isCategories}
            label="Categories"
            onChange={handleChange}
            displayEmpty
            renderValue={(selected) => selected.map(c => categories[c]?.name).join(', ')}
        >
            {
                getLUTValues(categories).map((cat, catIDX) => {
                    return (
                        <MenuItem key={catIDX} value={cat.id}>
                            <div style={{ background: cat.color}}>{cat.name}</div>
                        </MenuItem>
                    )
                })
            }
        </Select>
    );
}

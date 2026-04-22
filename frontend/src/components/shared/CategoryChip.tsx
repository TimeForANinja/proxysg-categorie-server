import React from 'react';
import {Chip, ChipProps, Tooltip} from '@mui/material';
import {colorToHex, getBackgroundColor} from '../../util/colormixer';
import {IConstraint} from "../../types/url";
import {formatConstraint} from "../../util/DateString";
import AccessTimeIcon from '@mui/icons-material/AccessTime';

interface SimpleCategory {
    name: string;
    color?: number;
}

interface CategoryChipProps extends Omit<ChipProps, 'label'> {
    category: SimpleCategory;
}

export const CategoryChip: React.FC<CategoryChipProps> = ({ 
    category,
    sx, 
    ...props 
}) => {
    let bgColor = null;
    let textColor = null;
    if (category.color) {
        bgColor = colorToHex(category.color);
        textColor = getBackgroundColor(bgColor);
    }

    return (
        <Chip
            label={category.name}
            size="small"
            variant="outlined"
            sx={{
                bgcolor: bgColor,
                color: textColor,
                fontWeight: 500,
                borderColor: bgColor,
                '& .MuiChip-label': { px: 1 },
                '& .MuiChip-icon': {
                    color: textColor
                },
                '& .MuiChip-deleteIcon': {
                    color: textColor,
                    opacity: 0.7,
                    '&:hover': {
                        color: textColor,
                        opacity: 1
                    }
                },
                ...sx
            }}
            {...props}
        />
    );
};

export const CategoryChipList: React.FC<{
    categories: {
        id: string,
        name: string,
        color: number,
    }[]
    constraints?: (IConstraint | undefined)[]
    limit?: number
    getItemProps?: (args: {index: number}) => any
}> = ({ categories, constraints, limit, getItemProps }) => {
    limit = limit ?? 4;
    const displayed = categories.slice(0, limit);
    const remaining = categories.length - limit;

    return (
        <>
            {
                displayed.map((category, index) => {
                    // fetch props and remove "key" from props
                    const props = getItemProps ? getItemProps({index}) : {};
                    const { key, ...rest } = props;

                    if (constraints && constraints[index] && (constraints[index].start || constraints[index]?.end)) {
                        const tt_title = formatConstraint(constraints[index])
                        rest.icon = (<AccessTimeIcon sx={{ fontSize: '14px !important' }} />);
                        return (
                            <Tooltip title={tt_title} key={category.id} placement="left">
                                <CategoryChip category={category} key={category.id} {...rest}/>
                            </Tooltip>
                        );
                    }
                    return <CategoryChip category={category} key={category.id} {...rest}/>;
                })
            }
            { remaining > 0 && (
                <Chip label={`+${remaining} more tags`} size="small" variant="outlined" />
            )}
        </>
    );
}

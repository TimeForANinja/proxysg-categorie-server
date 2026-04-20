import React from 'react';
import {Chip, ChipProps, Tooltip} from '@mui/material';
import {colorToHex, getBackgroundColor} from '../../util/colormixer';

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
    tooltips?: string[]
    limit?: number
    getItemProps?: (args: {index: number}) => any
}> = ({ categories, tooltips, limit, getItemProps }) => {
    limit = limit ?? 4;
    const displayed = categories.slice(0, limit);
    const remaining = categories.length - limit;

    return (
        <>
            {
                displayed.map((category, index) => {
                    const props = getItemProps ? getItemProps({index}) : {};
                    if (tooltips && tooltips[index]) {
                        return (
                            <Tooltip title={tooltips[index]} key={category.id}>
                                <CategoryChip category={category} key={category.id} {...props}/>
                            </Tooltip>
                        );
                    }
                    // remove key from props
                    const { key, ...rest } = props;
                    return <CategoryChip category={category} key={category.id} {...rest}/>;
                })
            }
            { remaining > 0 && (
                <Chip label={`+${remaining} more tags`} size="small" variant="outlined" />
            )}
        </>
    );
}

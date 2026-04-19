import React from 'react';
import {Chip, ChipProps} from '@mui/material';
import {ICategory} from '../../types/category';
import {getForegroundColor} from '../../util/colormixer';

interface CategoryChipProps extends Omit<ChipProps, 'label'> {
    category: ICategory | string;
    isBluecoat?: boolean;
}

export const CategoryChip: React.FC<CategoryChipProps> = ({ 
    category, 
    isBluecoat = false, 
    sx, 
    ...props 
}) => {
    if (!isBluecoat && typeof category !== 'string') {
        const bgColor = `#${category.color.toString(16).padStart(6, '0')}`;
        const textColor = getForegroundColor(bgColor);
        
        return (
            <Chip
                label={category.name}
                size="small"
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
    }

    const label = typeof category === 'string' ? category : category.name;
    
    return (
        <Chip
            label={label}
            size="small"
            variant={isBluecoat ? "filled" : "outlined"}
            sx={{ 
                fontWeight: isBluecoat ? 500 : 400,
                ...sx 
            }}
            {...props}
        />
    );
};

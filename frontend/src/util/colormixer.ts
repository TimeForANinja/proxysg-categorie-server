import chroma from 'chroma-js';

type PartialColorProfile = {
    bg: string,
    name: string,
}

type ColorProfile = {
    // foreground and background color
    fg: string,
    bg: string,
    // name of the color
    name: string,
}

type ColorLUT = Record<number, ColorProfile>;

// Function to calculate `fg` based on the contrast with the `bg`
const getForegroundColor = (backgroundColor: string): string => {
    // Calculate contrast with white (#FFFFFF) and black (#000000)
    const contrastWithWhite = chroma.contrast(backgroundColor, '#FFFFFF');
    const contrastWithBlack = chroma.contrast(backgroundColor, '#000000');

    // Return black or white based on which has better contrast
    return contrastWithWhite > contrastWithBlack ? '#FFFFFF' : '#000000';
};

const addFG = (partial: PartialColorProfile): ColorProfile => ({
    fg: getForegroundColor(partial.bg),
    bg: partial.bg,
    name: partial.name,
});

export const colorLUT: ColorLUT = {
    1:  addFG({ bg: '#00B8D9', name: 'Light Blue' }),
    2:  addFG({ bg: '#0052CC', name: 'Blue' }),
    3:  addFG({ bg: '#5243AA', name: 'Purple' }),
    4:  addFG({ bg: '#FF5630', name: 'Red' }),
    5:  addFG({ bg: '#FF8B00', name: 'Orange' }),
    6:  addFG({ bg: '#FFC400', name: 'Yellow' }),
    7:  addFG({ bg: '#36B37E', name: 'Light Green' }),
    8:  addFG({ bg: '#00875A', name: 'Green' }),
    9:  addFG({ bg: '#253858', name: 'Dark Blue' }),
    10: addFG({ bg: '#666666', name: 'Gray' }),
}

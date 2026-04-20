import chroma from 'chroma-js';

type PartialColorProfile = {
    fg: string,
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

// Function to calculate `bg` based on the contrast with the `fg`
export const getBackgroundColor = (backgroundColor: string): string => {
    // Calculate contrast with white (#FFFFFF) and black (#000000)
    const contrastWithWhite = chroma.contrast(backgroundColor, '#FFFFFF');
    const contrastWithBlack = chroma.contrast(backgroundColor, '#000000');

    // Return black or white based on which has the better contrast
    return contrastWithWhite > contrastWithBlack ? '#FFFFFF' : '#000000';
};

const addBG = (partial: PartialColorProfile): ColorProfile => ({
    bg: getBackgroundColor(partial.fg),
    fg: partial.fg,
    name: partial.name,
});

export const colorLUT: ColorLUT = {
    1:  addBG({ fg: '#00B8D9', name: 'Light Blue' }),
    2:  addBG({ fg: '#0052CC', name: 'Blue' }),
    3:  addBG({ fg: '#5243AA', name: 'Purple' }),
    4:  addBG({ fg: '#FF5630', name: 'Red' }),
    5:  addBG({ fg: '#FF8B00', name: 'Orange' }),
    6:  addBG({ fg: '#FFC400', name: 'Yellow' }),
    7:  addBG({ fg: '#36B37E', name: 'Light Green' }),
    8:  addBG({ fg: '#00875A', name: 'Green' }),
    9:  addBG({ fg: '#253858', name: 'Dark Blue' }),
    10: addBG({ fg: '#666666', name: 'Gray' }),
    11: addBG({ fg: '#BBBBBB', name: 'Light Gray' }),
}

export const colorToHex = (color: number): string => '#' + color.toString(16).padStart(6, '0');

export const hexToColor = (hex: string): number => parseInt(hex.replace('#', ''), 16);

export type LUT<T> = {
    [key: string]: T;
};

export const filterLUT = <T>(lut: LUT<T>, filter: (value: T) => boolean): LUT<T> => {
    const filtered: LUT<T> = {};
    for (const key in lut) {
        if (filter(lut[key])) {
            filtered[key] = lut[key];
        }
    }
    // Return a separate object - do not filter in-place
    return { ...filtered };
}

export const mapLUT = <T, U>(lut: LUT<T>, mapper: (value: T) => U): LUT<U> => {
    const mapped: LUT<U> = {};
    for (const key in lut) {
        mapped[key] = mapper(lut[key]);
    }
    return mapped;
}

export const pushLUT = <T extends { id: string }>(lut: LUT<T>, ...newElements: Array<T>): LUT<T> => {
    // clone the existing object - do not push in-place
    const updatedLUT: LUT<T> = { ...lut };
    for (const obj of newElements) {
        updatedLUT[obj.id] = obj;
    }
    return updatedLUT;
}

export const buildLUTFromID = <T extends { id: string }>(objects: Array<T>): LUT<T> => {
    const lut: LUT<T> = {};
    for (const obj of objects) {
        lut[obj.id] = obj;
    }
    return lut;
};

export const getLUTValues = <T>(lut: LUT<T>): Array<T> => Array.from(Object.values(lut));

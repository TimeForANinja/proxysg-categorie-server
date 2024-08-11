export type LUT<A> = {
    [key: number]: A;
};

export const buildLUTFromID = <T extends { id: number }>(objects: Array<T>): LUT<T> => {
    const lut: LUT<T> = {};
    for (const obj of objects) {
        lut[obj.id] = obj;
    }
    return lut;
};

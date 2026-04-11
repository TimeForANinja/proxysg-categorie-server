type TriStateType<T> = T | "closed" | "new";

export class TriState<T> {
    // Utility TriState Object
    // Allows edit Dialogue to be
    // a) Closed
    // b) Open for a new Object
    // c) Open to edit an existing Object

    public static CLOSED: TriState<any> = new TriState("closed");
    public static NEW: TriState<any> = new TriState("new");

    private readonly value: TriStateType<T>;

    constructor(value: TriStateType<T>) {
        this.value = value;
    }

    isOpen(): boolean {
        return this.value !== TriState.CLOSED.value;
    }

    isNull(): boolean {
        return this.value === TriState.NEW.value || !this.isOpen();
    }

    getValue(): T | null {
        if (this.isNull()) {
            return null;
        }
        return this.value as T;
    }
}
type comparing_result<Type> = {
    added: Type[],
    removed: Type[],

}

export function CompareLists<Type>(oldList: Type[], newList:Type[]): comparing_result<Type> {
    const added = newList.filter(x => oldList.indexOf(x) < 0);
    const removed = oldList.filter(x => newList.indexOf(x) < 0);
    return {
        added,
        removed,
    }
}

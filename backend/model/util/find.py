from typing import TypeVar, Callable, List, Tuple, Union

T = TypeVar("T")


def find_in_lists(objects: List[T], hashes: List[str], predicate: Callable[[T], bool]) -> Union[Tuple[T, str], Tuple[None, None]]:
    for idx, obj in enumerate(objects):
        if predicate(obj):
            return obj, hashes[idx]
    return None, None

def find_all_in_lists(objects: List[T], hashes: List[str], predicate: Callable[[T], bool]) -> Tuple[List[T], List[str]]:
    hit_obj = []
    hit_hash = []
    for idx, obj in enumerate(objects):
        if predicate(obj):
            hit_obj.append(obj)
            hit_hash.append(hashes[idx])
    return hit_obj, hit_hash

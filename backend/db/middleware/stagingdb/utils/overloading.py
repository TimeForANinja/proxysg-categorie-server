import time
from dataclasses import asdict
from typing import Optional, Dict, Any, TypeVar, Type, List, Callable

from auth.auth_user import AuthUser
from db.dbmodel.staging import ActionTable, ActionType, StagedChange
from db.middleware.stagingdb.cache import StagedCollection, StageFilter
from log import log_debug

# Generic type variables for different object types
T = TypeVar('T')


def get_and_overload_object(
    db_getter: Callable[[str], Optional[T]],
    staged: StagedCollection,
    action_table: ActionTable,
    obj_id: str,
    obj_class: Type[T]
) -> Optional[T]:
    """
    Get an object from the database or staging collection.

    Args:
        db_getter: A function that retrieves the object from the database
        staged: The staged collection
        action_table: The table the object belongs to
        obj_id: The unique ID of the object
        obj_class: The class to instantiate with the object data

    Returns:
        The object if found, None otherwise
    """
    # Try getting the object by id from the database
    db_obj = db_getter(obj_id)
    # Convert to dict (or None if not found in db)
    obj_data: Dict[str, Any] = asdict(db_obj) if db_obj is not None else None

    # query all staged changes that affect the object from the db
    relevant_staged_events = staged.get_filtered(
        StageFilter.fac_filter_table_id(action_table, obj_id)
    )

    if obj_data is None:
        # No object in DB, so check if we have an "add" event for the ID
        add_obj = StageFilter.first_or_default(
            relevant_staged_events,
            StageFilter.filter_add,
        )
        # save the data from the "add" event in obj_data
        obj_data = add_obj.data if add_obj is not None else None

        if obj_data is None:
            # no object in db, and no "add" event
            return None

        # set pending_changes since the object is staged
        obj_data.update({'pending_changes': True})

    # Overload any staged changes
    for staged_change in relevant_staged_events:
        if staged_change.data.get('is_deleted', 0) != 0:
            # we have a delete object so return "None"
            return None

        obj_data.update({'pending_changes': True})
        obj_data.update(staged_change.data)

    return obj_class(**obj_data)


def get_and_overload_all_objects(
        db_getter: Callable[[], List[T]],
        staged: StagedCollection,
        action_table: ActionTable,
        obj_class: Type[T]
) -> List[T]:
    """
    Get all objects of a specific type from the database and staging collection.

    Args:
        db_getter: A function that retrieves all objects from the database
        staged: The staged collection
        action_table: The table the objects belong to
        obj_class: The class to instantiate with the object data

    Returns:
        A list including all objects of the specified type
    """
    # Get all objects from the database
    db_objects: List[T] = db_getter()
    # Convert to dict
    objects: List[Dict[str, Any]] = [asdict(obj) for obj in db_objects]

    # load all (relevant) Staged Events from DB
    relevant_staged_events = staged.get_filtered(
        StageFilter.fac_filter_table(action_table),
    )

    # Prepare and append all "added" objects from the cache
    staged_obj = [
        o.data for o in
        StageFilter.apply(relevant_staged_events, StageFilter.filter_add)
    ]
    for obj in staged_obj: obj.update({'pending_changes': True})
    objects.extend(staged_obj)
    log_debug('get_all', 'fetched all data from db', {
        'existing objects': len(db_objects),
        'staged "add" objects': len(staged_obj),
        'staged changes': len(relevant_staged_events),
    })

    # group all non-ADD staged changes for this table by object id
    # as a source use the already cached relevant_staged_events
    # This allows us to quickly find all staged changes for a specific object,
    # without complex searching or db queries inside the for loop below
    changes_by_id: Dict[str, List[StagedChange]] = {}
    for sc in relevant_staged_events:
        if sc.action_type != ActionType.ADD:
            changes_by_id.setdefault(sc.uid, []).append(sc)

    # Go through all objects and overload any staged changes for that object
    staged_objects: List[T] = []
    for raw_object in objects:
        obj = raw_object

        for staged_change in changes_by_id.get(obj.get('id'), []):
            obj.update({'pending_changes': True})
            obj.update(staged_change.data)
            if staged_change.data.get('is_deleted', 0) != 0:
                # If any change marks deletion, we can stop the for loop
                break

        if obj.get('is_deleted', 0) == 0:
            # only append to staged_objects if not deleted
            staged_objects.append(obj_class(**obj))

    return staged_objects


def add_staged_change(
        action_type: ActionType,
        action_table: ActionTable,
        auth: AuthUser,
        obj_id: str,
        update_data: Dict[str, Any],
        staged: StagedCollection,
):
    """
    Create a staged change for an update/delete action and push it to the staging collection.

    Args:
        action_type: The type of action (ADD, UPDATE, DELETE)
        action_table: The table the object belongs to
        auth: The user who is performing the action
        obj_id: The unique ID of the object
        update_data: The data to update in the object
        staged: The staged collection
    """
    # Create a staged change
    staged_change = StagedChange(
        action_type=action_type,
        action_table=action_table,
        auth=auth,
        uid=obj_id,
        data=update_data,
        # only the timestamp is predefined
        timestamp=int(time.time()),
    )
    # Add the staged change to the staging DB
    staged.add(staged_change)


def add_staged_changes(
        action_type: ActionType,
        action_table: ActionTable,
        auth: AuthUser,
        obj_ids: List[str],
        update_data: List[Dict[str, Any]],
        staged: StagedCollection,
):
    """
    Create multiple staged change for an update/delete action and push it to the staging collection.
    Variant of add_staged_change for multiple objects.

    Args:
        action_type: The type of action (ADD, UPDATE, DELETE)
        action_table: The table the object belongs to
        auth: The user who is performing the action
        obj_ids: The unique ID of the object
        update_data: The data to update in the object
        staged: The staged collection
    """
    # Create the staged changes
    staged_changes = [
        StagedChange(
            action_type=action_type,
            action_table=action_table,
            auth=auth,
            uid=obj_ids[i],
            data=update_data[i],
            # only the timestamp is predefined
            timestamp=int(time.time()),
        )
        for i in range(len(obj_ids))
    ]
    # Add the staged changes to the staging DB
    staged.add_batch(staged_changes)


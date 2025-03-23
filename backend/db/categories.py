from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length


@dataclass(kw_only=True)
class MutableCategory:
    name: str = field(metadata={
        "required": True,
        "validate": Length(min=1),
        "description": "Name of the category",
    })
    color: int = field(metadata={
        "required": True,
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            "validate": Length(max=255),
            "description": "Description of the category"
        },
    )


@dataclass(kw_only=True)
class Category(MutableCategory):
    """
    Helper class to represent a category.
    """
    id: int = field(metadata={
        "required": True,
        "description": "ID of the category",
    })
    name: str = field(metadata={
        "required": True,
        "validate": Length(min=1),
        "description": "Name of the category",
    })
    color: int = field(metadata={
        "required": True,
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            "validate": Length(max=255),
            "description": "Description of the category"
        },
    )
    is_deleted: int = field(
        default=0,
        metadata={
            "description": "Whether the category is deleted or not",
        }
    )


class CategoriesDBInterface(ABC):
    @abstractmethod
    def create_table(self) -> None:
        """
        Create the 'categories' table if it doesn't exist.
        """
        pass

    @abstractmethod
    def add_category(self, category: MutableCategory) -> Category:
        """
        Add a new category with the given name, color, and an optional description.

        :param category: The (partial) category to add.
        :return: The newly created category.
        """
        pass

    @abstractmethod
    def get_category(self, category_id: int) -> Optional[Category]:
        """
        Retrieve the details of a specific category by its ID.

        :param category_id: The ID of the category to retrieve.
        :return: A Category
                 or None if the category doesn't exist or is marked as deleted.
        """
        pass

    @abstractmethod
    def update_category(
            self,
            cat_id: int,
            category: MutableCategory,
    ) -> Category:
        """
        Update the details of a specific category.

        :param cat_id: The ID of the category to update.
        :param category: The (partial) category to update.
        """
        pass

    @abstractmethod
    def delete_category(self, category_id: int) -> None:
        """
        Soft delete a category by setting its `is_deleted` flag to 1.

        :param category_id: The ID of the category to delete.
        """
        pass

    @abstractmethod
    def get_all_categories(self) -> List[Category]:
        """
        Retrieve all active categories that are not marked as deleted.

        :return: A list of categories
        """
        pass

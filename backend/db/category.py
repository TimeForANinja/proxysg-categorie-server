from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length

from db.util.validators import simpleNameValidator, simpleStringValidator


@dataclass(kw_only=True)
class MutableCategory:
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        'description': 'Name of the category',
    })
    color: int = field(metadata={
        'required': True,
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            'description': 'Description of the category'
        },
    )

@dataclass(kw_only=True)
class Category(MutableCategory):
    """
    Helper class to represent a category.
    """
    id: str = field(metadata={
        'required': True,
        'description': 'ID of the category',
    })
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        'description': 'Name of the category',
    })
    color: int = field(metadata={
        'required': True,
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            'description': 'Description of the category'
        },
    )
    is_deleted: int = field(
        default=0,
        metadata={
            'description': 'Whether the category is deleted or not',
        }
    )
    nested_categories: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of category IDs associated with the category',
        }
    )


class CategoryDBInterface(ABC):
    @abstractmethod
    def add_category(self, mut_cat: MutableCategory) -> Category:
        """
        Add a new category with the given name, color, and an optional description.

        :param mut_cat: The (partial) category to add.
        :return: The newly created category.
        """
        pass

    @abstractmethod
    def bulk_add_category(self, mut_cats: List[MutableCategory]) -> List[Category]:
        """
        Add a list of categories to the database.

        :param mut_cats: A list of categories to add.
        :return: A list of newly created categories.
        """
        pass

    @abstractmethod
    def get_category(self, category_id: str) -> Optional[Category]:
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
            cat_id: str,
            category: MutableCategory,
    ) -> Category:
        """
        Update the details of a specific category.

        :param cat_id: The ID of the category to update.
        :param category: The (partial) category to update.
        """
        pass

    @abstractmethod
    def delete_category(self, category_id: str) -> None:
        """
        Soft-delete a category by setting its `is_deleted` flag to the current timestamp.

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

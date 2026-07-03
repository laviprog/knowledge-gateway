from typing import Annotated

from fastapi import Depends, Query

DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100


class PaginationParams:
    """
    Shared ``limit``/``offset`` query parameters for list endpoints.
    """

    def __init__(
        self,
        limit: Annotated[
            int,
            Query(
                ge=1,
                le=MAX_PAGE_LIMIT,
                description="Maximum number of items to return.",
            ),
        ] = DEFAULT_PAGE_LIMIT,
        offset: Annotated[
            int,
            Query(ge=0, description="Number of items to skip."),
        ] = 0,
    ) -> None:
        self.limit = limit
        self.offset = offset


PaginationDep = Annotated[PaginationParams, Depends()]

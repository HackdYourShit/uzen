from typing import List, Union, cast

from tortoise.query_utils import Q

from uzen.models.rules import Rule
from uzen.services.searchers import AbstractSearcher


class RuleSearcher(AbstractSearcher):
    @classmethod
    async def search(
        cls, filters: dict, size=None, offset=None, id_only=False, count_only=False
    ) -> Union[List[Rule], List[int], int]:
        """Search rules.

        Arguments:
            filters {dict} -- Filters for rule search

        Keyword Arguments:
            size {[int]} -- Nmber of results returned (default: {None})
            offset {[int]} -- Offset of the first result for pagination (default: {None})
            id_only {bool} -- Whether to return only a list of ids (default: {False})
            count_only {bool} -- Whether to return only a count of results (default: {False})

        Returns:
            Union[List[Rule], List[int], int] -- A list of rules or count of the list
        """
        # build queirs from filters
        queries = []

        name = filters.get("name")
        if name is not None:
            queries.append(Q(name__contains=name))

        target = filters.get("target")
        if target is not None:
            queries.append(Q(target=target))

        source = filters.get("source")
        if source is not None:
            queries.append(Q(source__contains=source))

        query = Q(*queries)

        # Run search
        instance = cls(model=Rule, query=query)
        results = await instance._search(
            size=size, offset=offset, id_only=id_only, count_only=count_only
        )

        return cast(Union[List[Rule], List[int], int], results)

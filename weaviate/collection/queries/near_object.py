from typing import List, Optional, Type, Union

from weaviate.collection.classes.filters import (
    _Filters,
)
from weaviate.collection.classes.grpc import (
    MetadataQuery,
    PROPERTIES,
)
from weaviate.collection.classes.internal import (
    _Generative,
    _GenerativeReturn,
    _GroupBy,
    _GroupByReturn,
    _QueryReturn,
)
from weaviate.collection.classes.types import (
    Properties,
)
from weaviate.collection.queries.base import _Grpc
from weaviate.types import UUID


class _NearObjectQuery(_Grpc):
    def near_object(
        self,
        near_object: UUID,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[Union[PROPERTIES, Type[Properties]]] = None,
    ) -> _QueryReturn[Properties]:
        """Search for objects in this collection by another object using a vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#nearobject) for a more detailed explanation.

        Arguments:
            `near_object`
                The UUID of the object to search on, REQUIRED.
            `certainty`
                The minimum similarity score to return. If not specified, the default certainty specified by the server is used.
            `distance`
                The maximum distance to search. If not specified, the default distance specified by the server is used.
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by the server is returned.
            `auto_limit`
                The maximum number of [autocut](https://weaviate.io/developers/weaviate/api/graphql/additional-operators#autocut) results to return. If not specified, no limit is applied.
            `filters`
                The filters to apply to the search.
            `return_metadata`
                The metadata to return for each object.
            `return_properties`
                The properties to return for each object.

        Returns:
            A `_QueryReturn` object that includes the searched objects.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties = self._parse_return_properties(return_properties)
        res = self._query().near_object(
            near_object=near_object,
            certainty=certainty,
            distance=distance,
            limit=limit,
            autocut=auto_limit,
            filters=filters,
            return_metadata=return_metadata,
            return_properties=ret_properties,
        )
        return self._result_to_query_return(res, return_properties)


class _NearObjectGenerate(_Grpc):
    def near_object(
        self,
        near_object: UUID,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[Union[PROPERTIES, Type[Properties]]] = None,
    ) -> _GenerativeReturn[Properties]:
        """Perform retrieval-augmented generation (RaG) on the results of a by-object object search in this collection using a vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#nearobject) for a more detailed explanation.

        Arguments:
            `near_object`
                The UUID of the object to search on, REQUIRED.
            `certainty`
                The minimum similarity score to return. If not specified, the default certainty specified by the server is used.
            `distance`
                The maximum distance to search. If not specified, the default distance specified by the server is used.
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by the server is returned.
            `auto_limit`
                The maximum number of [autocut](https://weaviate.io/developers/weaviate/api/graphql/additional-operators#autocut) results to return. If not specified, no limit is applied.
            `filters`
                The filters to apply to the search.
            `return_metadata`
                The metadata to return for each object.
            `return_properties`
                The properties to return for each object.

        Returns:
            A `_GenerativeReturn` object that includes the searched objects with per-object generated results and group generated results.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties = self._parse_return_properties(return_properties)
        res = self._query().near_object(
            near_object=near_object,
            certainty=certainty,
            distance=distance,
            limit=limit,
            autocut=auto_limit,
            filters=filters,
            generative=_Generative(
                single=single_prompt,
                grouped=grouped_task,
                grouped_properties=grouped_properties,
            ),
            return_metadata=return_metadata,
            return_properties=ret_properties,
        )
        return self._result_to_generative_return(res, return_properties)


class _NearObjectGroupBy(_Grpc):
    def near_object(
        self,
        near_object: UUID,
        group_by_property: str,
        number_of_groups: int,
        objects_per_group: int,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[Union[PROPERTIES, Type[Properties]]] = None,
    ) -> _GroupByReturn[Properties]:
        """Group the results of a by-object object search in this collection using a vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#nearobject) for a more detailed explanation.

        Arguments:
            `near_object`
                The UUID of the object to search on, REQUIRED.
            `group_by_property`
                The property to group by, REQUIRED.
            `number_of_groups`
                The number of groups to return, REQUIRED.
            `objects_per_group`
                The number of objects to return per group, REQUIRED.
            `certainty`
                The minimum similarity score to return. If not specified, the default certainty specified by the server is used.
            `distance`
                The maximum distance to search. If not specified, the default distance specified by the server is used.
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by the server is returned.
            `auto_limit`
                The maximum number of [autocut](https://weaviate.io/developers/weaviate/api/graphql/additional-operators#autocut) results to return. If not specified, no limit is applied.
            `filters`
                The filters to apply to the search.
            `return_metadata`
                The metadata to return for each object.
            `return_properties`
                The properties to return for each object.

         Returns:
            A `_GroupByReturn` object that includes the searched objects grouped by the specified property.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties = self._parse_return_properties(return_properties)
        res = self._query().near_object(
            near_object=near_object,
            certainty=certainty,
            distance=distance,
            limit=limit,
            autocut=auto_limit,
            filters=filters,
            group_by=_GroupBy(
                prop=group_by_property,
                number_of_groups=number_of_groups,
                objects_per_group=objects_per_group,
            ),
            return_metadata=return_metadata,
            return_properties=ret_properties,
        )
        return self._result_to_groupby_return(res, return_properties)

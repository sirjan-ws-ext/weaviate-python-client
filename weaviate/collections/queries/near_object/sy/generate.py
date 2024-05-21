from typing import Generic, List, Optional

from weaviate.collections.classes.filters import (
    _Filters,
)
from weaviate.collections.classes.grpc import METADATA, GroupBy, Rerank
from weaviate.collections.classes.internal import (
    GenerativeNearMediaReturnType,
    ReturnProperties,
    ReturnReferences,
)
from weaviate.collections.classes.types import Properties, TProperties, References, TReferences
from weaviate.collections.queries.base_sync import _BaseGenerate
from weaviate.types import NUMBER, INCLUDE_VECTOR, UUID


class _NearObjectGenerate(Generic[Properties, References], _BaseGenerate[Properties, References]):
    def near_object(
        self,
        near_object: UUID,
        *,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        certainty: Optional[NUMBER] = None,
        distance: Optional[NUMBER] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        group_by: Optional[GroupBy] = None,
        rerank: Optional[Rerank] = None,
        target_vector: Optional[str] = None,
        include_vector: INCLUDE_VECTOR = False,
        return_metadata: Optional[METADATA] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
        return_references: Optional[ReturnReferences[TReferences]] = None,
    ) -> GenerativeNearMediaReturnType[Properties, References, TProperties, TReferences]:
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
            `offset`
                The offset to start from. If not specified, the retrieval begins from the first object in the server.
            `auto_limit`
                The maximum number of [autocut](https://weaviate.io/developers/weaviate/api/graphql/additional-operators#autocut) results to return. If not specified, no limit is applied.
            `filters`
                The filters to apply to the search.
            `rerank`
                How the results should be reranked. NOTE: A `rerank-*` module must be enabled for this functionality to work.
            `include_vector`
                Whether to include the vector in the results. If not specified, this is set to False.
            `return_metadata`
                The metadata to return for each object, defaults to `None`.
            `return_properties`
                The properties to return for each object.
            `return_references`
                The references to return for each object.

        NOTE:
            - If `return_properties` is not provided then all properties are returned except for blob properties.
            - If `return_metadata` is not provided then no metadata is provided. Use MetadataQuery.full() to retrieve all metadata.
            - If `return_references` is not provided then no references are provided.

        Returns:
            A `_GenerativeNearMediaReturn` object that includes the searched objects with per-object generated results and group generated results.

        Raises:
            `weaviate.exceptions.WeaviateGRPCQueryError`:
                If the request to the Weaviate server fails.
        """
        return self._loop.run_until_complete(
            self._generate.near_object,
            near_object=near_object,
            single_prompt=single_prompt,
            grouped_task=grouped_task,
            grouped_properties=grouped_properties,
            certainty=certainty,
            distance=distance,
            limit=limit,
            offset=offset,
            auto_limit=auto_limit,
            filters=filters,
            group_by=group_by,
            rerank=rerank,
            target_vector=target_vector,
            include_vector=include_vector,
            return_metadata=return_metadata,
            return_properties=return_properties,
            return_references=return_references,
        )
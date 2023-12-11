from typing import Generic, Optional, Type, cast, overload

from weaviate.collections.classes.filters import (
    FilterMetadata,
)
from weaviate.collections.classes.grpc import PROPERTIES, MetadataQuery

from weaviate.collections.classes.internal import (
    _MetadataSingleObjectReturn,
    _ObjectSingleReturn,
    QuerySingleObjectReturn,
    ReturnProperties,
    _QueryOptions,
)
from weaviate.collections.classes.types import Properties, TProperties
from weaviate.collections.queries.base import _Grpc
from weaviate.types import UUID
from typing_extensions import is_typeddict


class _FetchObjectByIDQuery(Generic[Properties], _Grpc[Properties]):
    @overload
    def fetch_object_by_id(
        self,
        uuid: UUID,
        include_vector: bool = False,
        *,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _ObjectSingleReturn[Properties]:
        ...

    @overload
    def fetch_object_by_id(
        self,
        uuid: UUID,
        include_vector: bool = False,
        *,
        return_properties: Type[TProperties],
    ) -> _ObjectSingleReturn[TProperties]:
        ...

    def fetch_object_by_id(
        self,
        uuid: UUID,
        include_vector: bool = False,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> Optional[QuerySingleObjectReturn[Properties, TProperties]]:
        """Retrieve an object from the server by its UUID.

        Arguments:
            `uuid`
                The UUID of the object to retrieve, REQUIRED.
            `return_properties`
                The properties to return for each object.
            `include_vector`
                Whether to include the vector in the returned object.

        Raises:
            `weaviate.exceptions.WeaviateQueryException`:
                If the network connection to Weaviate fails.
            `weaviate.exceptions.WeaviateInsertInvalidPropertyError`:
                If a property is invalid. I.e., has name `id` or `vector`, which are reserved.
        """
        return_metadata = MetadataQuery(
            creation_time_unix=True, last_update_time_unix=True, is_consistent=True
        )
        res = self._query().get(
            limit=1,
            filters=FilterMetadata.ById.equal(uuid),
            return_metadata=self._parse_return_metadata(return_metadata, include_vector),
            return_properties=self._parse_return_properties(return_properties),
        )
        objects = self._result_to_query_return(
            res,
            return_properties,
            _QueryOptions.from_input(return_metadata, return_properties, include_vector),
        )

        if len(objects.objects) == 0:
            return None

        obj = objects.objects[0]
        assert obj.metadata is not None
        assert obj.metadata.creation_time_unix is not None
        assert obj.metadata.last_update_time_unix is not None

        if is_typeddict(return_properties):
            return _ObjectSingleReturn[TProperties](
                uuid=obj.uuid,
                vector=obj.vector,
                properties=cast(TProperties, obj.properties),
                metadata=_MetadataSingleObjectReturn(
                    creation_time_unix=obj.metadata.creation_time_unix,
                    last_update_time_unix=obj.metadata.last_update_time_unix,
                    is_consistent=obj.metadata.is_consistent,
                ),
            )
        else:
            return _ObjectSingleReturn[Properties](
                uuid=obj.uuid,
                vector=obj.vector,
                properties=cast(Properties, obj.properties),
                metadata=_MetadataSingleObjectReturn(
                    creation_time_unix=obj.metadata.creation_time_unix,
                    last_update_time_unix=obj.metadata.last_update_time_unix,
                    is_consistent=obj.metadata.is_consistent,
                ),
            )
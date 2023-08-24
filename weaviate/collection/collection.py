from typing import Any, Dict, Generic, Optional, Type

from weaviate.collection.classes import CollectionConfig, Properties
from weaviate.collection.collection_base import CollectionBase
from weaviate.collection.config import _ConfigCollection
from weaviate.collection.data import _DataCollection
from weaviate.collection.grpc import _GrpcCollection
from weaviate.collection.tenants import _Tenants
from weaviate.connect import Connection
from weaviate.data.replication import ConsistencyLevel
from weaviate.util import _capitalize_first_letter


class CollectionObject(Generic[Properties]):
    def __init__(
        self,
        connection: Connection,
        name: str,
        type_: Type[Properties],
        consistency_level: Optional[ConsistencyLevel] = None,
        tenant: Optional[str] = None,
    ) -> None:
        self._connection = connection
        self.name = name
        self.__type = type_

        self.config = _ConfigCollection(self._connection, name)
        self.data = _DataCollection[Properties](
            connection, name, self.config, consistency_level, tenant, type_
        )
        self.query = _GrpcCollection(connection, name, tenant)
        self.tenants = _Tenants(connection, name)

        self.__tenant = tenant
        self.__consistency_level = consistency_level

    def with_tenant(self, tenant: Optional[str] = None) -> "CollectionObject[Properties]":
        return CollectionObject[Properties](
            self._connection, self.name, self.__type, self.__consistency_level, tenant
        )

    def with_consistency_level(
        self, consistency_level: Optional[ConsistencyLevel] = None
    ) -> "CollectionObject[Properties]":
        return CollectionObject[Properties](
            self._connection, self.name, self.__type, consistency_level, self.__tenant
        )


class Collection(CollectionBase):
    def create(
        self, config: CollectionConfig, type_: Type[Properties] = Dict[str, Any]
    ) -> CollectionObject[Properties]:
        name = super()._create(config)
        if config.name != name:
            raise ValueError(
                f"Name of created collection ({name}) does not match given name ({config.name})"
            )
        return self.get(name, type_)

    def get(
        self, name: str, type_: Type[Properties] = Dict[str, Any]
    ) -> CollectionObject[Properties]:
        return CollectionObject[Properties](self._connection, name, type_)

    def delete(self, name: str) -> None:
        """Use this method to delete a collection from the Weaviate instance by its name.

        WARNING: If you have instances of client.collection_model.get() or client.collection_model.create()
        for this collection within your code, they will be cease to function correctly after this operation.

        Parameters:
        - name: The name of the collection to delete.
        """
        self._delete(_capitalize_first_letter(name))

    def exists(self, name: str) -> bool:
        return self._exists(_capitalize_first_letter(name))
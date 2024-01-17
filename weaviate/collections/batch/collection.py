import asyncio
from typing import Generic, List, Optional, Sequence, Union

from weaviate.collections.batch.base import _BatchBase, _BatchDataWrapper
from weaviate.collections.batch.batch_wrapper import _BatchWrapper
from weaviate.collections.classes.config import ConsistencyLevel
from weaviate.collections.classes.internal import ReferenceInputs, ReferenceInput
from weaviate.collections.classes.types import Properties
from weaviate.connect import ConnectionV4
from weaviate.types import UUID


class _BatchCollection(Generic[Properties], _BatchBase):
    def __init__(
        self,
        connection: ConnectionV4,
        consistency_level: Optional[ConsistencyLevel],
        results: _BatchDataWrapper,
        event_loop: asyncio.AbstractEventLoop,
        fixed_batch_size: Optional[int],
        fixed_concurrent_requests: Optional[int],
        name: str,
        tenant: Optional[str] = None,
    ) -> None:
        super().__init__(
            connection=connection,
            consistency_level=consistency_level,
            results=results,
            event_loop=event_loop,
            fixed_batch_size=fixed_batch_size,
            fixed_concurrent_requests=fixed_concurrent_requests,
        )
        self.__name = name
        self.__tenant = tenant

    def add_object(
        self,
        properties: Optional[Properties] = None,
        references: Optional[ReferenceInputs] = None,
        uuid: Optional[UUID] = None,
        vector: Optional[Sequence] = None,
    ) -> UUID:
        """Add one object to this batch.

        NOTE: If the UUID of one of the objects already exists then the existing object will be replaced by the new object.

        Arguments:
            `properties`
                The data properties of the object to be added as a dictionary.
            `references`
                The references of the object to be added as a dictionary. Use `wvc.Reference.to` to create the correct values in the dict.
            `uuid`:
                The UUID of the object as an uuid.UUID object or str. It can be a Weaviate beacon or Weaviate href.
                If it is None an UUIDv4 will generated, by default None
            `vector`:
                The embedding of the object that should be validated. Can be used when a collection does not have a vectorization module or the given vector was generated using the _identical_ vectorization module that is configured for the class. In this case this vector takes precedence. Supported types are `list`, 'numpy.ndarray`, `torch.Tensor` and `tf.Tensor`, by default None.

        Returns:
            `str`
                The UUID of the added object. If one was not provided a UUIDv4 will be auto-generated for you and returned here.

        Raises:
            `WeaviateBatchValidationError`
                If the provided options are in the format required by Weaviate.
        """
        return self._add_object(
            collection=self.__name,
            properties=properties,
            references=references,
            uuid=uuid,
            vector=vector,
            tenant=self.__tenant,
        )

    def add_reference(
        self, from_uuid: UUID, from_property: str, to: Union[ReferenceInput, List[UUID]]
    ) -> None:
        """Add a reference to this batch.

        Arguments:
            `from_uuid`
                The UUID of the object, as an uuid.UUID object or str, that should reference another object.
            `from_property`
                The name of the property that contains the reference.
            `to`
                The UUID of the referenced object, as an uuid.UUID object or str, that is actually referenced.
                For multi-target references use wvc.Reference.to_multi_targer().

        Raises:
            `WeaviateBatchValidationError`
                If the provided options are in the format required by Weaviate.
        """
        self._add_reference(
            from_uuid,
            self.__name,
            from_property,
            to,
            self.__tenant,
        )


class _BatchCollectionWrapper(Generic[Properties], _BatchWrapper):
    def __init__(
        self,
        connection: ConnectionV4,
        consistency_level: Optional[ConsistencyLevel],
        name: str,
        tenant: Optional[str] = None,
    ) -> None:
        super().__init__(connection, consistency_level)
        self.__name = name
        self.__tenant = tenant

    def __enter__(self) -> _BatchCollection[Properties]:
        loop = self._open_async_connection()

        self._current_batch = _BatchCollection[Properties](
            connection=self._connection,
            consistency_level=self._consistency_level,
            results=self._batch_data,
            fixed_batch_size=self._batch_size,
            fixed_concurrent_requests=self._concurrent_requests,
            name=self.__name,
            tenant=self.__tenant,
            event_loop=loop,
        )
        return self._current_batch

    def configure_fixed_size(
        self,
        batch_size: int = 100,
        concurrent_requests: int = 2,
    ) -> None:
        """Configure fixed size batches. Note that the default is dynamic batching.

        When you exit the context manager, the final batch will be sent automatically.

        Arguments:
            `batch_size`
                The number of objects/references to be sent in one batch. If not provided, the default value is 100.
            `concurrent_requests`
                The number of concurrent requests when sending batches. This controls the number of concurrent requests
                made to Weaviate and not the speed of batch creation within Python.
        """
        self._batch_size = batch_size
        self._concurrent_requests = concurrent_requests

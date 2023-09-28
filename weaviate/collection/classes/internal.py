import sys
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, Union, cast

import uuid as uuid_package

if sys.version_info < (3, 9):
    from typing_extensions import Annotated, get_type_hints, get_origin
else:
    from typing import Annotated, get_type_hints, get_origin

from weaviate.collection.collection_base import _CollectionObjectBase
from weaviate.collection.classes.grpc import (
    FromReference,
    FromReferenceMultiTarget,
    MetadataQuery,
    PROPERTIES,
    Generate,
)
from weaviate.collection.classes.types import Properties, P
from weaviate.util import _to_beacons
from weaviate.types import UUIDS

from weaviate_grpc import weaviate_pb2


@dataclass
class _MetadataResult:
    uuid: Optional[uuid_package.UUID]
    vector: Optional[List[float]]
    creation_time_unix: Optional[int]
    last_update_time_unix: Optional[int]
    distance: Optional[float]
    certainty: Optional[float]
    score: Optional[float]
    explain_score: Optional[str]
    is_consistent: Optional[bool]
    generative: Optional[str]

    def _to_return(self) -> "_MetadataReturn":
        return _MetadataReturn(
            uuid=self.uuid,
            vector=self.vector,
            creation_time_unix=self.creation_time_unix,
            last_update_time_unix=self.last_update_time_unix,
            distance=self.distance,
            certainty=self.certainty,
            score=self.score,
            explain_score=self.explain_score,
            is_consistent=self.is_consistent,
        )


@dataclass
class _MetadataReturn:
    uuid: Optional[uuid_package.UUID]
    vector: Optional[List[float]]
    creation_time_unix: Optional[int]
    last_update_time_unix: Optional[int]
    distance: Optional[float]
    certainty: Optional[float]
    score: Optional[float]
    explain_score: Optional[str]
    is_consistent: Optional[bool]


@dataclass
class _Object(Generic[P]):
    properties: P
    metadata: _MetadataReturn


@dataclass
class _GroupByObject(Generic[P], _Object[P]):
    belongs_to_group: str


@dataclass
class _GenerativeObject(Generic[P], _Object[P]):
    generated: Optional[str]


@dataclass
class _GenerativeReturn(Generic[P]):
    objects: List[_GenerativeObject[P]]
    generated: Optional[str]


@dataclass
class _GroupByResult(Generic[P]):
    name: str
    min_distance: float
    max_distance: float
    number_of_objects: int
    objects: List[_Object[P]]


@dataclass
class _GroupByReturn(Generic[P]):
    objects: List[_GroupByObject[P]]
    groups: Dict[str, _GroupByResult]


@dataclass
class _QueryReturn(Generic[P]):
    objects: List[_Object[P]]


class _Generative:
    single: Optional[str]
    grouped: Optional[str]
    grouped_properties: Optional[List[str]]

    def __init__(
        self,
        single: Optional[str],
        grouped: Optional[str],
        grouped_properties: Optional[List[str]],
    ) -> None:
        self.single = single
        self.grouped = grouped
        self.grouped_properties = grouped_properties

    def to_grpc(self) -> weaviate_pb2.GenerativeSearch:
        return weaviate_pb2.GenerativeSearch(
            single_response_prompt=self.single,
            grouped_response_task=self.grouped,
            grouped_properties=self.grouped_properties,
        )

    @classmethod
    def from_input(cls, generate: Optional[Generate]) -> Optional["_Generative"]:
        return (
            cls(
                single=generate.single_prompt,
                grouped=generate.grouped_task,
                grouped_properties=generate.grouped_properties,
            )
            if generate
            else None
        )


class _GroupBy:
    prop: str
    number_of_groups: int
    objects_per_group: int

    def __init__(self, prop: str, number_of_groups: int, objects_per_group: int) -> None:
        self.prop = prop
        self.number_of_groups = number_of_groups
        self.objects_per_group = objects_per_group

    def to_grpc(self) -> weaviate_pb2.GroupBy:
        return weaviate_pb2.GroupBy(
            path=[self.prop],
            number_of_groups=self.number_of_groups,
            objects_per_group=self.objects_per_group,
        )


class _Reference(Generic[P]):
    def __init__(
        self,
        objects: Optional[List[_Object[P]]],
        target_collection: Optional[str],
        uuids: Optional[UUIDS],
    ):
        """You should not initialise this class directly. Use the `.to()` or `.to_multi_target()` class methods instead."""
        self.__objects = objects
        self.__target_collection = target_collection if target_collection else ""
        self.__uuids = uuids

    def _to_beacons(self) -> List[Dict[str, str]]:
        if self.__uuids is None:
            return []
        return _to_beacons(self.__uuids, self.__target_collection)

    @classmethod
    def _from(cls, objects: List[_Object[P]]) -> "_Reference[P]":
        return cls(objects, None, None)

    @property
    def is_multi_target(self) -> bool:
        """Returns True if the reference is to a multi-target collection."""
        return self.__target_collection != ""

    @property
    def uuids_str(self) -> List[str]:
        """Returns the UUIDs as strings."""
        if isinstance(self.__uuids, list):
            return [str(uid) for uid in self.__uuids]
        else:
            return [str(self.__uuids)]

    @property
    def target_collection(self) -> str:
        """Returns the target collection name."""
        return self.__target_collection

    @property
    def objects(self) -> List[_Object[P]]:
        """Returns the objects of the cross reference."""
        return self.__objects or []


Reference = _Reference[P]


class ReferenceFactory:
    """Factory class for cross references to other objects.

    Can be used with or without generics. If used with generics, the type of the cross reference can be defined from
    which the nested relationship will be used when performing queries using the generics. If used without generics,
    all returned objects will of the`Dict[str, Any]` type.
    """

    @classmethod
    def to(cls, uuids: UUIDS, data_model: Optional[Type[P]] = None) -> Reference[P]:
        """Define cross references to other objects by their UUIDs.

        Can be made to be generic by supplying a type to the `data_model` argument.

        Arguments:
            uuids
                List of UUIDs of the objects to which the reference should point.
        """
        return _Reference[P](None, None, uuids)

    @classmethod
    def to_multi_target(
        cls,
        uuids: UUIDS,
        target_collection: Union[str, _CollectionObjectBase],
        data_model: Optional[Type[P]] = None,
    ) -> Reference[P]:
        """Define cross references to other objects by their UUIDs and the collection in which they are stored.

        Can be made to be generic by supplying a type to the `data_model` argument.

        Arguments:
            uuids
                List of UUIDs of the objects to which the reference should point.
            target_collection
                The collection in which the objects are stored. Can be either the name of the collection or the collection object itself.
        """
        return _Reference[P](
            None,
            target_collection.name
            if isinstance(target_collection, _CollectionObjectBase)
            else target_collection,
            uuids,
        )


def _metadata_from_dict(metadata: Dict[str, Any]) -> _MetadataReturn:
    return _MetadataReturn(
        uuid=uuid_package.UUID(metadata["id"]) if "id" in metadata else None,
        vector=metadata.get("vector"),
        creation_time_unix=metadata.get("creationTimeUnix"),
        last_update_time_unix=metadata.get("lastUpdateTimeUnix"),
        distance=metadata.get("distance"),
        certainty=metadata.get("certainty"),
        explain_score=metadata.get("explainScore"),
        score=metadata.get("score"),
        is_consistent=metadata.get("isConsistent"),
    )


def _extract_property_type_from_reference(type_: _Reference[P]) -> Type[P]:
    """Extract inner type from Reference[Properties]."""
    if getattr(type_, "__origin__", None) == _Reference:
        args = cast(List[Type[P]], getattr(type_, "__args__", None))
        return args[0]
    raise ValueError("Type is not Reference[Properties]")


def _extract_property_type_from_annotated_reference(
    type_: Union[
        Annotated[_Reference[P], MetadataQuery],
        Annotated[_Reference[P], MetadataQuery, str],
    ]
) -> Type[P]:
    """Extract inner type from Annotated[Reference[Properties]]."""
    if get_origin(type_) is Annotated:
        args = cast(List[_Reference[Type[P]]], getattr(type_, "__args__", None))
        inner_type = args[0]
        if get_origin(inner_type) is _Reference:
            inner_args = cast(List[Type[P]], getattr(inner_type, "__args__", None))
            return inner_args[0]
    raise ValueError("Type is not Annotated[Reference[Properties]]")


def __create_link_to_from_annotated_reference(
    link_on: str,
    value: Union[
        Annotated[_Reference[Properties], MetadataQuery],
        Annotated[_Reference[Properties], MetadataQuery, str],
    ],
) -> Union[FromReference, FromReferenceMultiTarget]:
    """Create FromReference or FromReferenceMultiTarget from Annotated[Reference[Properties]]."""
    assert get_origin(value) is Annotated
    args = cast(List[_Reference[Properties]], getattr(value, "__args__", None))
    inner_type = args[0]
    assert get_origin(inner_type) is _Reference
    inner_type_metadata = cast(
        Union[Tuple[MetadataQuery], Tuple[MetadataQuery, str]], getattr(value, "__metadata__", None)
    )
    metadata = inner_type_metadata[0]
    if len(inner_type_metadata) == 2:
        target_collection = cast(Tuple[MetadataQuery, str], inner_type_metadata)[
            1
        ]  # https://github.com/python/mypy/issues/1178
        return FromReferenceMultiTarget(
            link_on=link_on,
            return_metadata=metadata,
            return_properties=_extract_properties_from_data_model(
                _extract_property_type_from_annotated_reference(value)
            ),
            target_collection=target_collection,
        )
    else:
        return FromReference(
            link_on=link_on,
            return_metadata=metadata,
            return_properties=_extract_properties_from_data_model(
                _extract_property_type_from_annotated_reference(value)
            ),
        )


def __create_link_to_from_reference(
    link_on: str,
    value: _Reference[Properties],
) -> FromReference:
    """Create FromReference from Reference[Properties]."""
    return FromReference(
        link_on=link_on,
        return_metadata=MetadataQuery(),
        return_properties=_extract_properties_from_data_model(
            _extract_property_type_from_reference(value)
        ),
    )


def _extract_properties_from_data_model(type_: Type[Properties]) -> PROPERTIES:
    """Extract properties of Properties recursively from Properties.

    Checks to see if there is a _Reference[Properties] or Annotated[_Reference[Properties]] in the data model and
    lists out the non-cross-reference properties.
    """
    return [
        __create_link_to_from_annotated_reference(key, value)
        if get_origin(value) is Annotated
        else (
            __create_link_to_from_reference(key, value) if get_origin(value) is _Reference else key
        )
        for key, value in get_type_hints(type_, include_extras=True).items()
    ]

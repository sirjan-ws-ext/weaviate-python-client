import io
import json
import pathlib

from typing import Callable, List, Optional, TypeVar, Union, cast
from typing_extensions import ParamSpec

from weaviate.collection.classes.aggregate import (
    MetricsQuery,
    AProperties,
    AggregateResult,
    AggregateBool,
    AggregateDate,
    AggregateInt,
    AggregateFloat,
    AggregateRef,
    AggregateStr,
    _AggregateGroupByReturn,
    _AggregateReturn,
    _Metrics,
    _MetricsBase,
    _MetricsBool,
    _MetricsDate,
    _MetricsFloat,
    _MetricsInt,
    _MetricsRef,
    _MetricsStr,
    _GroupedBy,
    TopOccurrence,
)
from weaviate.collection.classes.config import ConsistencyLevel
from weaviate.collection.classes.filters import _Filters
from weaviate.collection.classes.grpc import Move
from weaviate.connect import Connection
from weaviate.collection.extract_filters import _FilterToREST
from weaviate.exceptions import WeaviateQueryException
from weaviate.gql.aggregate import AggregateBuilder
from weaviate.util import file_encoder_b64
from weaviate.types import UUID

P = ParamSpec("P")
T = TypeVar("T")


def validate(fn: Callable[P, T]) -> Callable[P, T]:
    """Validate the aggregations argument."""

    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            aggregations = args[1]
        except IndexError:
            aggregations = kwargs.get("return_metrics")
        if not isinstance(aggregations, list):
            raise TypeError(
                f"The aggregations argument received an unexpected type: {type(aggregations)}. This argument must be a list!"
            )
        for aggregation in aggregations:
            if not isinstance(aggregation, _MetricsBase):
                raise TypeError(
                    f"One of the aggregations is an unexpected type: {type(aggregation)}. Did you forget to append .returning() to .with_()?"
                )
        return fn(*args, **kwargs)

    return inner


class _Aggregate:
    def __init__(
        self,
        connection: Connection,
        name: str,
        consistency_level: Optional[ConsistencyLevel],
        tenant: Optional[str],
    ):
        self.__connection = connection
        self.__name = name
        self._tenant = tenant
        self._consistency_level = consistency_level

    def _query(self) -> AggregateBuilder:
        return AggregateBuilder(self.__name, self.__connection)

    def _to_aggregate_result(
        self, response: dict, metrics: Optional[MetricsQuery]
    ) -> _AggregateReturn:
        try:
            result: dict = response["data"]["Aggregate"][self.__name][0]
            return _AggregateReturn(
                properties=self.__parse_properties(result, metrics) if metrics is not None else {},
                total_count=result["meta"]["count"] if result.get("meta") is not None else None,
            )
        except KeyError as e:
            raise ValueError(
                f"There was an error accessing the {e} key when parsing the GraphQL response: {response}"
            )

    def _to_group_by_result(
        self, response: dict, metrics: Optional[MetricsQuery]
    ) -> List[_AggregateGroupByReturn]:
        try:
            results: dict = response["data"]["Aggregate"][self.__name]
            return [
                _AggregateGroupByReturn(
                    grouped_by=_GroupedBy(
                        prop=result["groupedBy"]["path"][0],
                        value=result["groupedBy"]["value"],
                    ),
                    properties=self.__parse_properties(result, metrics)
                    if metrics is not None
                    else {},
                    total_count=result["meta"]["count"] if result.get("meta") is not None else None,
                )
                for result in results
            ]
        except KeyError as e:
            raise ValueError(
                f"There was an error accessing the {e} key when parsing the GraphQL response: {response}"
            )

    def __parse_properties(self, result: dict, metrics: MetricsQuery) -> AProperties:
        props: AProperties = {}
        for metric in metrics:
            if metric.property_name in result:
                props[metric.property_name] = self.__parse_property(
                    result[metric.property_name], metric
                )
        return props

    @staticmethod
    def __parse_property(property_: dict, metric: _Metrics) -> AggregateResult:
        if isinstance(metric, _MetricsStr):
            return AggregateStr(
                count=property_.get("count"),
                top_occurrences=[
                    TopOccurrence(
                        occurs=cast(dict, top_occurence).get("occurs"),
                        value=cast(dict, top_occurence).get("value"),
                    )
                    for top_occurence in property_.get("topOccurrences", [])
                ],
            )
        elif isinstance(metric, _MetricsInt):
            return AggregateInt(
                count=property_.get("count"),
                maximum=property_.get("maximum"),
                mean=property_.get("mean"),
                median=property_.get("median"),
                mode=property_.get("mode"),
                sum_=property_.get("sum"),
            )
        elif isinstance(metric, _MetricsFloat):
            return AggregateFloat(
                count=property_.get("count"),
                maximum=property_.get("maximum"),
                mean=property_.get("mean"),
                median=property_.get("median"),
                mode=property_.get("mode"),
                sum_=property_.get("sum"),
            )
        elif isinstance(metric, _MetricsBool):
            return AggregateBool(
                count=property_.get("count"),
                percentage_false=property_.get("percentageFalse"),
                percentage_true=property_.get("percentageTrue"),
                total_false=property_.get("totalFalse"),
                total_true=property_.get("totalTrue"),
            )
        elif isinstance(metric, _MetricsDate):
            return AggregateDate(
                count=property_.get("count"),
                maximum=property_.get("maximum"),
                median=property_.get("median"),
                minimum=property_.get("minimum"),
                mode=property_.get("mode"),
            )
        elif isinstance(metric, _MetricsRef):
            return AggregateRef(pointing_to=property_.get("pointingTo"))
        else:
            raise ValueError(
                f"Unknown aggregation type {metric} encountered in _Aggregate.__parse_property() for property {property_}"
            )

    def _base(
        self,
        metrics: Optional[MetricsQuery] = None,
        filters: Optional[_Filters] = None,
        limit: Optional[int] = None,
        total_count: bool = False,
    ) -> AggregateBuilder:
        builder = self._query()
        if metrics is not None:
            builder = builder.with_fields(" ".join([metric.to_gql() for metric in metrics]))
        if filters is not None:
            builder = builder.with_where(_FilterToREST.convert(filters))
        if limit is not None:
            builder = builder.with_limit(limit)
        if total_count:
            builder = builder.with_meta_count()
        if self._tenant is not None:
            builder = builder.with_tenant(self._tenant)
        return builder

    @staticmethod
    def _do(query: AggregateBuilder) -> dict:
        res = query.do()
        if res.get("errors") is not None:
            raise WeaviateQueryException(
                f"Error in GraphQL response: {json.dumps(res['errors'], indent=2)}, for the following query: {query.build()}"
            )
        return res

    @staticmethod
    def _add_near_image(
        builder: AggregateBuilder,
        near_image: Union[str, pathlib.Path, io.BufferedReader],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        object_limit: Optional[int] = None,
    ) -> AggregateBuilder:
        payload: dict = {}
        payload["image"] = _parse_media(near_image)
        if certainty is not None:
            payload["certainty"] = certainty
        if distance is not None:
            payload["distance"] = distance
        builder = builder.with_near_image(payload, encode=False)
        if object_limit is not None:
            builder = builder.with_object_limit(object_limit)
        return builder

    @staticmethod
    def _add_near_object(
        builder: AggregateBuilder,
        near_object: UUID,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        object_limit: Optional[int] = None,
    ) -> AggregateBuilder:
        payload: dict = {}
        payload["id"] = str(near_object)
        if certainty is not None:
            payload["certainty"] = certainty
        if distance is not None:
            payload["distance"] = distance
        builder = builder.with_near_object(payload)
        if object_limit is not None:
            builder = builder.with_object_limit(object_limit)
        return builder

    @staticmethod
    def _add_near_text(
        builder: AggregateBuilder,
        query: Union[List[str], str],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        move_to: Optional[Move] = None,
        move_away: Optional[Move] = None,
        object_limit: Optional[int] = None,
    ) -> AggregateBuilder:
        payload: dict = {}
        payload["concepts"] = query if isinstance(query, list) else [query]
        if certainty is not None:
            payload["certainty"] = certainty
        if distance is not None:
            payload["distance"] = distance
        if move_to is not None:
            payload["moveTo"] = move_to._to_gql_payload()
        if move_away is not None:
            payload["moveAwayFrom"] = move_away._to_gql_payload()
        builder = builder.with_near_text(payload)
        if object_limit is not None:
            builder = builder.with_object_limit(object_limit)
        return builder

    @staticmethod
    def _add_near_vector(
        builder: AggregateBuilder,
        near_vector: List[float],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        object_limit: Optional[int] = None,
    ) -> AggregateBuilder:
        payload: dict = {}
        payload["vector"] = near_vector
        if certainty is not None:
            payload["certainty"] = certainty
        if distance is not None:
            payload["distance"] = distance
        builder = builder.with_near_vector(payload)
        if object_limit is not None:
            builder = builder.with_object_limit(object_limit)
        return builder


def _parse_media(media: Union[str, pathlib.Path, io.BufferedReader]) -> str:
    if isinstance(media, str):  # if already encoded by user
        return media
    else:
        return file_encoder_b64(media)

import hashlib
import typing
import uuid as uuid_package
from dataclasses import dataclass
from enum import Enum
from typing import Union, Dict, Any, Optional, List, Type, Set, TypeVar, TypeAlias

from pydantic import BaseModel, Field, field_validator

UUID: TypeAlias = Union[str, uuid_package.UUID]
NUMBERS: TypeAlias = Union[int, float]

PYTHON_TYPE_TO_DATATYPE = {"text": str, str: "text", "int": int, int: "int"}


class DataType(str, Enum):
    TEXT = "text"
    TEXT_ARRAY = "text[]"
    INT = "int"
    INT_ARRAY = "int[]"
    BOOL = "boolean"
    BOOL_ARRAY = "boolean[]"
    NUMBER = "number"
    NUMBER_ARRAY = "number[]"
    DATE = "date"
    DATE_ARRAY = "date[]"
    UUID = "uuid"
    UUID_ARRAY = "uuid[]"
    GEO_COORDINATES = "geoCoordinates"
    BLOB = "blob"
    PHONE_NUMBER = "phoneNumber"


def python_type_to_datatype(datatype: type) -> str:
    if datatype == str:
        return DataType.TEXT.value
    elif datatype == List[str]:
        return DataType.TEXT_ARRAY.value
    else:
        return DataType.INT.value


class VectorIndexType(str, Enum):
    HNSW = "hnsw"


class Tokenization(str, Enum):
    WORD = "word"
    WHITESPACE = "whitespace"
    LOWERCASE = "lowercase"
    FIELD = "field"


class Vectorizer(str, Enum):
    NONE = "none"
    TEXT2VEC_OPENAI = "text2vec-openai"
    TEXT2VEC_COHERE = "text2vec-cohere"
    TEXT2VEC_PALM = "text2vec-palm"
    TEXT2VEC_HUGGINGFACE = "text2vec-huggingface"
    TEXT2VEC_TRANSFORMERS = "text2vec-transformers"
    TEXT2VEC_CONTEXTIONARY = "text2vec-contextionary"
    IMG2VEC_NEURAL = "img2vec-neural"
    MULTI2VEC_CLIP = "multi2vec-clip"
    REF2VEC_CENTROID = "ref2vec_centroid"


class VectorDistance(str, Enum):
    COSINE = "cosine"
    DOT = "dot"
    L2_SQUARED = "l2-squared"
    HAMMING = "hamming"
    MANHATTAN = "manhattan"


class StopwordsPreset(str, Enum):
    NONE = "none"
    EN = "en"


ModuleConfig = Dict[Vectorizer, Dict[str, Any]]


@dataclass
class VectorIndexConfig(BaseModel):
    distance: VectorDistance = VectorDistance.COSINE
    efConstruction: int = 128
    maxConnections: int = 64


@dataclass
class ShardingConfig(BaseModel):
    virtualPerPhysical: Optional[int] = None
    desiredCount: Optional[int] = None
    actualCount: Optional[int] = None
    desiredVirtualCount: Optional[int] = None
    actualVirtualCount: Optional[int] = None
    key: Optional[str] = None
    strategy: Optional[str] = None
    function: Optional[str] = None


class ReplicationConfig(BaseModel):
    factor: Optional[int] = None


class BM25config(BaseModel):
    b: float = 0.75
    k1: float = 1.2


class Stopwords(BaseModel):
    preset: StopwordsPreset = StopwordsPreset.EN
    additions: Optional[List[str]] = None
    removals: Optional[List[str]] = None


class InvertedIndexConfig(BaseModel):
    bm25: Optional[BM25config] = None
    stopwords: Optional[Stopwords] = None
    indexTimestamps: bool = False
    indexPropertyLength: bool = False
    indexNullState: bool = False


class BaseProperty(BaseModel):
    uuid: UUID = Field(default=uuid_package.uuid4())
    vector: Optional[List[float]] = None

    def props_to_dict(self) -> Dict[str, Any]:
        return {
            name: value
            for name, value in self.model_fields.items()
            if name not in BaseProperty.model_fields
        }

    @field_validator("uuid")
    def create_valid_uuid(cls, input_uuid: UUID) -> uuid_package.UUID:
        if isinstance(input_uuid, uuid_package.UUID):
            return input_uuid

        # see if str is already a valid uuid
        try:
            return uuid_package.UUID(input_uuid)
        except ValueError:
            hex_string = hashlib.md5(input_uuid.encode("UTF-8")).hexdigest()
            return uuid_package.UUID(hex=hex_string)

    @staticmethod
    def type_to_dict(model: Type["BaseProperty"]) -> List[Dict[str, Any]]:
        types = typing.get_type_hints(model)
        return [
            {
                "name": name.capitalize(),
                "dataType": [
                    PYTHON_TYPE_TO_DATATYPE[BaseProperty._remove_optional_type(types[name])]
                ],
            }
            for name, value in model.model_fields.items()
            if name not in BaseProperty.model_fields
        ]

    @staticmethod
    def _remove_optional_type(python_type: Type[type]) -> Type[type]:
        args = typing.get_args(python_type)
        if len(args) == 0:
            return python_type

        return [t for t in args if t is not None][0]


class CollectionConfigBase(BaseModel):
    name: str
    vectorIndexType: Optional[VectorIndexType] = None
    vectorizer: Optional[Vectorizer] = None
    vectorIndexConfig: Optional[VectorIndexConfig] = None
    description: Optional[str] = None
    shardingConfig: Optional[ShardingConfig] = None
    replicationConfig: Optional[ReplicationConfig] = None
    invertedIndexConfig: Optional[InvertedIndexConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        ret_dict = {"class": self.name.capitalize()}

        for cls_field in self.model_fields:
            val = getattr(self, cls_field)
            if cls_field in ["name", "properties"] or val is None:
                continue
            if isinstance(val, Enum):
                ret_dict[cls_field] = str(val.value)
            elif isinstance(val, (bool, float, str, int)):
                ret_dict[cls_field] = str(val)
            else:
                ret_dict[cls_field] = val.to_dict()

        return ret_dict


Model = TypeVar("Model", bound=BaseProperty)


class CollectionConfigModel(CollectionConfigBase):
    properties: Type[Model]

    def to_dict(self) -> Dict[str, Any]:
        ret_dict = super().to_dict()
        ret_dict["properties"] = self.properties.type_to_dict(self.properties)

        return ret_dict


class Property(BaseModel):
    name: str
    dataType: DataType
    indexFilterable: Optional[bool] = None
    indexSearchable: Optional[bool] = None
    tokenization: Optional[Tokenization] = None
    description: Optional[str] = None
    moduleConfig: Optional[ModuleConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        ret_dict = super().model_dump(exclude_none=True)
        ret_dict["dataType"] = [ret_dict["dataType"]]
        return ret_dict


class CollectionConfig(CollectionConfigBase):
    properties: Optional[List[Property]] = None

    def to_dict(self) -> Dict[str, Any]:
        ret_dict = super().to_dict()
        if self.properties is not None:
            ret_dict["properties"] = [prop.to_dict() for prop in self.properties]

        return ret_dict


class Metadata(BaseModel):
    vector: bool = False
    distance: bool = False
    certainty: bool = False
    score: bool = False
    explain_score: bool = Field(alias="explainScore", default=False)
    is_consistent: bool = Field(alias="isConsistent", default=False)

    def _get_fields(self) -> Set[str]:
        additional_props: Set[str] = set()
        for field, value in self.model_fields.items():
            enabled: bool = getattr(self, field)
            if enabled:
                name = value.alias if value.alias is not None else field
                additional_props.add(name)
        return additional_props

    def to_graphql(self) -> str:
        additional_props = self._get_fields()
        if len(additional_props) > 0:
            return "_additional{" + " ".join(additional_props) + "}"
        else:
            return ""

    def to_rest(self) -> str:
        return ",".join(self._get_fields())


class MetadataReturn(BaseModel):
    uuid: Optional[UUID] = Field(None, alias="id")
    vector: Optional[List[float]] = None
    creation_time_unix: Optional[int] = Field(None, alias="creationTimeUnix")
    last_update_time_unix: Optional[int] = Field(None, alias="lastUpdateTimeUnix")
    distance: Optional[float] = None
    certainty: Optional[float] = None
    score: Optional[float] = None
    explain_score: Optional[str] = Field(None, alias="explainScore")
    is_consistent: Optional[bool] = Field(None, alias="isConsistent")

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_UNSPECIFIED: _ClassVar[Result]
    RESULT_ERROR: _ClassVar[Result]
    RESULT_WARNING: _ClassVar[Result]
    RESULT_PASS: _ClassVar[Result]
    RESULT_FAILURE: _ClassVar[Result]
RESULT_UNSPECIFIED: Result
RESULT_ERROR: Result
RESULT_WARNING: Result
RESULT_PASS: Result
RESULT_FAILURE: Result

class Parameter(_message.Message):
    __slots__ = ("name", "description", "selected_value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SELECTED_VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    selected_value: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., selected_value: _Optional[str] = ...) -> None: ...

class Check(_message.Message):
    __slots__ = ("name", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Rule(_message.Message):
    __slots__ = ("name", "description", "check", "parameter")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CHECK_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    check: Check
    parameter: Parameter
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., check: _Optional[_Union[Check, _Mapping]] = ..., parameter: _Optional[_Union[Parameter, _Mapping]] = ...) -> None: ...

class Policy(_message.Message):
    __slots__ = ("rules", "parameters")
    RULES_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    rules: _containers.RepeatedCompositeFieldContainer[Rule]
    parameters: _containers.RepeatedCompositeFieldContainer[Parameter]
    def __init__(self, rules: _Optional[_Iterable[_Union[Rule, _Mapping]]] = ..., parameters: _Optional[_Iterable[_Union[Parameter, _Mapping]]] = ...) -> None: ...

class Subject(_message.Message):
    __slots__ = ("title", "resource_id", "result", "evaluated_on", "reason")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    EVALUATED_ON_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    title: str
    resource_id: str
    result: Result
    evaluated_on: _timestamp_pb2.Timestamp
    reason: str
    def __init__(self, title: _Optional[str] = ..., resource_id: _Optional[str] = ..., result: _Optional[_Union[Result, str]] = ..., evaluated_on: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., reason: _Optional[str] = ...) -> None: ...

class ObservationByCheck(_message.Message):
    __slots__ = ("name", "description", "check_id", "methods", "collected_at", "subjects", "evidence_refs")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CHECK_ID_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    COLLECTED_AT_FIELD_NUMBER: _ClassVar[int]
    SUBJECTS_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_REFS_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    check_id: str
    methods: _containers.RepeatedScalarFieldContainer[str]
    collected_at: _timestamp_pb2.Timestamp
    subjects: _containers.RepeatedCompositeFieldContainer[Subject]
    evidence_refs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., check_id: _Optional[str] = ..., methods: _Optional[_Iterable[str]] = ..., collected_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., subjects: _Optional[_Iterable[_Union[Subject, _Mapping]]] = ..., evidence_refs: _Optional[_Iterable[str]] = ...) -> None: ...

class Finding(_message.Message):
    __slots__ = ("name", "description", "related_observations")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    RELATED_OBSERVATIONS_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    related_observations: _containers.RepeatedCompositeFieldContainer[ObservationByCheck]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., related_observations: _Optional[_Iterable[_Union[ObservationByCheck, _Mapping]]] = ...) -> None: ...

class PVPResult(_message.Message):
    __slots__ = ("observations", "links")
    class LinksEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    OBSERVATIONS_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    observations: _containers.RepeatedCompositeFieldContainer[ObservationByCheck]
    links: _containers.ScalarMap[str, str]
    def __init__(self, observations: _Optional[_Iterable[_Union[ObservationByCheck, _Mapping]]] = ..., links: _Optional[_Mapping[str, str]] = ...) -> None: ...

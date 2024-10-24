import c2p.framework.models.models_pb2 as _models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSchemaRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetSchemaResponse(_message.Message):
    __slots__ = ("json_schema",)
    JSON_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    json_schema: bytes
    def __init__(self, json_schema: _Optional[bytes] = ...) -> None: ...

class ConfigureRequest(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: bytes
    def __init__(self, config: _Optional[bytes] = ...) -> None: ...

class ConfigureResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class RemediationRequest(_message.Message):
    __slots__ = ("findings",)
    FINDINGS_FIELD_NUMBER: _ClassVar[int]
    findings: _containers.RepeatedCompositeFieldContainer[_models_pb2.Finding]
    def __init__(self, findings: _Optional[_Iterable[_Union[_models_pb2.Finding, _Mapping]]] = ...) -> None: ...

class RemediationResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class GenerateRequest(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: _models_pb2.Policy
    def __init__(self, policy: _Optional[_Union[_models_pb2.Policy, _Mapping]] = ...) -> None: ...

class GenerateResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class ScanRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ScanResponse(_message.Message):
    __slots__ = ("result", "error")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    result: _models_pb2.PVPResult
    error: str
    def __init__(self, result: _Optional[_Union[_models_pb2.PVPResult, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

from pydantic import BaseModel, field_serializer
from enum import Enum, StrEnum
from typing import Literal, Any
from http import HTTPStatus
from base64 import b64encode


class AdmissionReviewBase(BaseModel):
    apiVersion: Literal["admission.k8s.io/v1"] 
    kind: Literal["AdmissionReview"]

class JsonPatchOp(Enum):
    Add = "add"
    Remove = "remove"
    Replace = "replace"
    Copy = "Copy"
    Move = "Move"
    Test = "Text"

class Operation(StrEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CONNECT= "CONNECT"

class JsonPatch(BaseModel):
    op: JsonPatchOp
    path: str
    value: str | None

class ResponseStatus(BaseModel):
    code: HTTPStatus
    message: str

class Response(BaseModel):
    uid: str
    allowed: bool
    status: ResponseStatus | None = None
    warnings: list[str] | None = None
    patchType: Literal["JSONPatch"] | None = None
    patch: list[JsonPatch] | None = None

    @field_serializer("patch")
    def base64_patch(self, patches):
        if patches is not None:            
            return b64encode(bytearray(f"[{",".join([patch.model_dump_json() for patch in patches])}]",encoding="utf-8"))
        return patches
    
class AdmissionReviewResponse(AdmissionReviewBase):
    response: Response

class Kind(BaseModel):
    group: str
    version: str
    kind: str

class Resource(BaseModel):
    group: str
    version: str
    resource: str

class UserInfo(BaseModel):
    username: str
    uid: str | None = None
    groups: list[str]
    extra: dict[Any,Any]

class Object(BaseModel):
    apiVersion: str
    kind: str

class Request(BaseModel):
    uid: str
    kind: Kind
    resource: Resource
    subResource: str | None = None
    requestKind: Kind
    requestResource: Resource
    requestSubResource: str | None = None
    name: str | None = None
    namespace: str
    operation: Operation
    userInfo: UserInfo
    object: Object | None = None
    oldObject: Object | None = None
    options: Object | None = None
    dryRun: bool

class AdmissionReviewRequest(AdmissionReviewBase):
    request: Request
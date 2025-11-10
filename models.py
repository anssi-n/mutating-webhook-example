from pydantic import BaseModel, field_serializer, Field
from enum import Enum, StrEnum
from typing import Literal, Any
from http import HTTPStatus
from base64 import b64encode
from datetime import datetime

type NoneType = 'None'

class AdmissionReviewBase(BaseModel):
    apiVersion: Literal["admission.k8s.io/v1"] 
    kind: Literal["AdmissionReview"]

class JsonPatchOp(Enum):
    Add = "add"
    Remove = "remove"
    Replace = "replace"
    Copy = "copy"
    Move = "move"
    Test = "text"

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

class Metadata(BaseModel):
    namespace: str  | None = None
    name: str | None = None
    uid: str | None = None
    labels: dict[str,str] | None = None
    annotations: dict[str,str] | None = None
    resourceVersion: str | None = None
    generation: int | None = None
    creationTimestamp: datetime | str | None = None
    deletionTimestamp: datetime | str | None = None

class VolumeMount(BaseModel):
    name: str
    readOnly: bool | None = None
    mountPath: str

class Capability(BaseModel):
     add: list[str] | None = None
     remove: list[str] |None = None

class SecurityContext(BaseModel):
    runAsUser: int | None = None
    runAsGroup: int | None = None
    supplementalGroups: list[int] | None = None
    supplementalGroupsPolicy: str | None = None
    fsGroup: int | None = None
    fsGroupChangePolicy: str | None = None
    allowPrivilegeEscalation: bool | None = None
    capabilities: Capability | None = None

class ResourceRequest(BaseModel):
    cpu: str | int | None = None
    memory: str | int | None = None
    storage: str | None = None

class Resources(BaseModel):
    limits: ResourceRequest | None = None
    requests: ResourceRequest | None = None
    
class Ref(BaseModel):
    name: str
    key: str

class ValueFrom(BaseModel):
    configMapKeyRef: Ref | None = None
    secretKeyRef: Ref | None = None

class Env(BaseModel):
    name: str
    value: str | None = None
    valueFrom: ValueFrom | None = None

class Ports(BaseModel):
    name: str | None = None
    protocol: str | None = None
    port: int | None = None
    containerPort: int | None = None

class Container(BaseModel):
    name: str
    image: str
    ports: list[Ports] | None = None
    env: list[Env] | None = None
    resources: Resources | None = None
    volumeMounts: list[VolumeMount]
    securityContext: SecurityContext | None = None
    terminationMessagePath: str
    terminationMessagePolicy: str
    imagePullPolicy: str

class Toleration(BaseModel):
    key: str
    operator: str
    effect: str
    tolerationSeconds: int

class VolumeItems(BaseModel):
    key: str
    path: str

class SecretVolume(BaseModel):
    secretName: str
    items: list[VolumeItems] | None = None
    defaultMode: int | None = None
    optional: bool | None = None

class ConfigMapVolume(BaseModel):
    name: str
    items: list[VolumeItems] | None = None
    defaultMode: int | None = None
    optional: bool | None = None    

class EmptyDirVolume(BaseModel):
    sizeLimit: str | None = None
    medium: str | None = None

class GitRepoVolume(BaseModel):
    repository: str
    revision: str

class HostPathVolume(BaseModel):
    path: str 
    type: str | None = None                     

class ImageVolume(BaseModel):
    reference: str
    pullPolicy: str | None = None

class NfsVolume(BaseModel):
    server: str
    path: str
    readOnly: bool | None = None

class PersistentVolumeClaimVolume(BaseModel):
    claimName: str

class Volume(BaseModel):
    name: str
    secret: SecretVolume | None = None
    configMap: ConfigMapVolume | None = None
    projected: Any | None = None
    emptyDir: EmptyDirVolume | None = None
    gitRepo: GitRepoVolume | None = None
    hostPath: HostPathVolume | None = None
    image: ImageVolume | None = None
    nfs: NfsVolume | None = None
    persistentVolumeClaim: PersistentVolumeClaimVolume | None = None

class MatchExpression(BaseModel):
    key: str
    operator: str
    values: list[str]    

class Selector(BaseModel):
    matchLabels: dict[str,str] | None = None
    matchExpressions: list[MatchExpression] | None = None

class Template(BaseModel):
    metadata: Metadata
    spec: "Spec"

class Spec(BaseModel):
    containers: list[Container] | None = None
    volumes: list[Volume] | None = None
    replicas: int | None = None
    selector: Selector | None = None
    template: Template | None = None
    volumeClaimTemplates: list[Template] | None = None
    accessModes: list[str] | None = None
    storageClassName: str | None = None
    volumeMode: str | None = None
    resources: Resources | None = None
    restartPolicy: str | None = None
    terminationGracePeriodSeconds: int | None = None
    dnsPolicy: str | None = None
    serviceAccountName: str | None = None
    serviceAccount: str | None = None
    securityContext: SecurityContext | None = None
    schedulerName: str | None = None
    tolerations: list[Toleration] | None = None
    priority: int | None = None
    enableServiceLinks: bool | None = None
    preemptionPolicy: str | None = None

    
class Status(BaseModel):
    phase: str | None = None
    qosClass: str | None = None

class Object(BaseModel):
    apiVersion: str
    kind: str
    metadata: Metadata | None = None
    data: dict[str,str] | None = None
    stringData: dict[str,str] | None = None
    spec: Spec | None = None
    status: Status | None = None
    fieldManager: str | None = None

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
    object_: Object | str = Field(default='None', alias="object")
    oldObject: Object | str | None
    options: Object | str 
    dryRun: bool

class AdmissionReviewRequest(AdmissionReviewBase):
    request: Request
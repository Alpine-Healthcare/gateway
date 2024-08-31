from datetime import datetime
from pydantic import BaseModel, Field 
from dataclasses import dataclass, field
from typing import List, Optional
from webauthn.helpers.structs import AuthenticatorTransport
import base64

ALPINE_ID = "VMWz3UWdXvd4uy+h4jpfsOG2KuZpcLy0Nuj4GhoajkE="

'''
Data Interfaces
'''
@dataclass
class Credential():
    id: str
    public_key: str
    sign_count: int
    transports: Optional[List[AuthenticatorTransport]] = None


'''
Core Graph Data Structures
'''

class AccessKey(BaseModel):
    access_key: str
    encryption_key: str


class EncryptionKeys(BaseModel):
    access_key: AccessKey
    encryption_key: str


class Edge(BaseModel):
    type: Optional[str]
    child_hash_id: Optional[str]


class PDFSNode(BaseModel):
    type: Optional[str]
    hash_id: Optional[str] 
    is_root: Optional[bool] = False
    edges: Optional[dict[str, Optional[Edge]]]



class BinaryDataManifest(BaseModel):
    required: bool = False




'''
Nodes and Edges
'''

class N_TreatmentBinary(PDFSNode):
    type = "N_TreatmentBinary"
    name: str = "2 Weight Watcher"
    detail: str = "Tracks your weight and gives updates on progress towards your weight goal."
    data_manifest: dict[str, BinaryDataManifest] = { }
    frequency: str = ""
    execution_binaries: dict[str, str] = { }


class N_Treatment_I(PDFSNode):
    type = "N_Treatment_"
    treatment : str = ""

    is_active: bool = True
    active_on: str = ""

    edges: dict[str, Optional[Edge]] = {
        "e_out_TreatmentBinary": None
    }

    def init_instance(self, instanceType: str):
        self.treatment = instanceType
        self.type = "N_Treatment_" + instanceType


class N_DataGroup_I(PDFSNode):
    type = "N_DataGroup_"
    metric: str = ''
    edges: dict[str, Optional[Edge]] = {}
    records: dict[str, float]

    def init_instance(self, instanceType: str):
        self.type = instanceType
        self.type = "N_DataGroup_" + instanceType


class N_DataManifest(PDFSNode):
    type = "N_DataManifest"
    edges: dict[str, Optional[Edge]] = {}


class N_TreatmentManifest(PDFSNode):
    type = "N_TreatmentManifest"
    edges: dict[str, Optional[Edge]] = {}


class N_AccessPackage(PDFSNode):
    type = "N_AccessPackage"
    key: str


class N_Inbox(PDFSNode):
    type = "N_Inbox"
    unread_messages: List[str] = []


class N_UserAccount(PDFSNode):
    type = "N_UserAccount"
    is_root = True

    credentials: List[Credential] 

    edges: dict[str, Optional[Edge]] = {
        "e_out_AccessPackage": None,
        "e_out_TreatmentManifest": None,
        "e_out_DataManifest": None,
        "e_out_Inbox": None,
    }

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        expectedEdges = None
        for key in dir(N_UserAccount):
            if key == "__fields__":
                expectedEdges = getattr(N_UserAccount, key)["edges"].default

        for key in expectedEdges:
            if key not in self.edges:
                self.edges[key] = None

class AlpineNodeManifestUser(BaseModel):
    hash_id: str
    timestamp: float

class AlpineNodeManifest(BaseModel):
    users: dict[str, AlpineNodeManifestUser] = {}


'''
Graph Mapper
'''
class NetworkMapperClass(BaseModel):
    node ={
        "N_Inbox": N_Inbox,
        "N_AccessPackage": N_AccessPackage,
        "N_UserAccount": N_UserAccount,
        "N_DataManifest": N_DataManifest,
        "N_DataGroup_I": N_DataGroup_I,
        "N_TreatmentManifest": N_TreatmentManifest,
        "N_Treatment_I": N_Treatment_I,
        "N_TreatmentBinary": N_TreatmentBinary,
    }


    def getName(name):
        name.split("_")[1]

NetworkMapper = NetworkMapperClass()
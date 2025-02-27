from datetime import datetime
from pydantic import BaseModel, Field 
from dataclasses import dataclass, field
from typing import Dict, List, Optional
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


class Edge(BaseModel):
    type: Optional[str]
    child_hash_id: Optional[str]


class PDFSNode(BaseModel):
    type: Optional[str]
    hash_id: Optional[str]
    edges: Optional[dict[str, Optional[Edge]]]
    data: Optional[str] = None



class BinaryDataManifest(BaseModel):
    required: bool = False



class Message(BaseModel):
    sentOn: str
    sender: str
    message: str


'''
Nodes and Edges
'''
class N_TreatmentProgress(PDFSNode):
    type = "N_TreatmentProgress"


class N_TreatmentInstance_I(PDFSNode):
    type = "N_TreatmentInstance_I"

    #Encrypt
    date: str = ""
    messages: List[Message] = []
    media: Optional[str] = None

    def init_instance(self, instanceType: str):
        self.type = "N_TreatmentInstance_" + instanceType


class TreatmentIntake(BaseModel):
    type: str
    title: str
    value: Optional[str | int]

class N_TreatmentBinary(PDFSNode):
    type = "N_TreatmentBinary"

    #Encrypt
    name: str = ""
    detail: str = ""
    data_manifest: dict[str, BinaryDataManifest] = { }
    frequency: str = ""
    execution_binary: str = "" 
    intake: Dict[str, TreatmentIntake]

class N_Treatment_I(PDFSNode):
    type = "N_Treatment_"
    edges: dict[str, Optional[Edge]] = {
        "e_out_TreatmentBinary": None
    }

    def init_instance(self, instanceType: str):
        self.type = "N_Treatment_" + instanceType


class N_DataGroup_I(PDFSNode):
    type = "N_DataGroup_"
    edges: dict[str, Optional[Edge]] = {}

    def init_instance(self, instanceType: str):
        self.type = "N_DataGroup_" + instanceType


class N_DataManifest(PDFSNode):
    type = "N_DataManifest"
    edges: dict[str, Optional[Edge]] = {}


class N_TreatmentManifest(PDFSNode):
    type = "N_TreatmentManifest"
    edges: dict[str, Optional[Edge]] = {}




class N_Inbox(PDFSNode):
    type = "N_Inbox"

    #Encrypt
    #unread_messages: List[Message] = []


class AccessPackage(BaseModel):
    ciphertext: str
    dataToEncryptHash: str

class N_UserAccount(PDFSNode):
    type = "N_UserAccount"
    is_root = True

    edges: dict[str, Optional[Edge]] = {
        "e_out_TreatmentManifest": None,
        "e_out_DataManifest": None,
        "e_out_Inbox": None,
    }

    access_package: Optional[AccessPackage] = None

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

        "N_UserAccount": N_UserAccount,

        "N_DataManifest": N_DataManifest,
        "N_DataGroup_I": N_DataGroup_I,


        "N_TreatmentManifest": N_TreatmentManifest,
        "N_Treatment_I": N_Treatment_I,
        "N_TreatmentInstance_I": N_TreatmentInstance_I,
        "N_TreatmentBinary": N_TreatmentBinary,
    }


    def getName(name):
        name.split("_")[1]

NetworkMapper = NetworkMapperClass()
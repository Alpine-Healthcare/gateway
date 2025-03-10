from pydantic import BaseModel
from typing import Dict, List, Optional

'''
Core Graph Data Structures
'''

class Edge(BaseModel):
    type: Optional[str]
    child_hash_id: Optional[str]


class PDOSNode(BaseModel):
    type: Optional[str]
    hash_id: Optional[str] = None
    edges: Optional[dict[str, Optional[Edge]]] = None
    data: Optional[str] = None

class N_PDOSStorageNode(PDOSNode):
    type: Optional[str] = "N_PDOSStorageNode_I"
    def init_instance(self, instanceType: str):
        self.type = "N_PDOSStorageNode_" + instanceType

class BinaryDataManifest(BaseModel):
    required: bool = False


class Message(BaseModel):
    sentOn: str
    sender: str
    message: str


'''
Nodes and Edges
'''
class N_TreatmentProgress(PDOSNode):
    type: Optional[str] = "N_TreatmentProgress"

class N_TreatmentEncounter(PDOSNode):
    type: Optional[str] = "N_TreatmentEncounter"


class N_TreatmentInstance_I(PDOSNode):
    type: Optional[str] = "N_TreatmentInstance_I"

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


class N_TreatmentBinary(PDOSNode):
    type: Optional[str] = "N_TreatmentBinary"

    #Encrypt
    name: str = ""
    owner: str = ""
    group: str = ""
    detail: str = ""
    description: str = ""
    data_manifest: dict[str, BinaryDataManifest] = { }
    frequency: str = ""
    execution_binary: str = "" 
    intake: Dict[str, TreatmentIntake]

class N_Treatment_I(PDOSNode):
    type: Optional[str] = "N_Treatment_"
    edges: dict[str, Optional[Edge]] = {
        "e_out_TreatmentBinary": None
    }

    def init_instance(self, instanceType: str):
        self.type = "N_Treatment_" + instanceType


class N_DataGroup_I(PDOSNode):
    type: Optional[str] = "N_DataGroup_"
    edges: dict[str, Optional[Edge]] = {}

    def init_instance(self, instanceType: str):
        self.type = "N_DataGroup_" + instanceType


class N_DataManifest(PDOSNode):
    type: Optional[str] = "N_DataManifest"
    edges: dict[str, Optional[Edge]] = {}


class N_TreatmentManifest(PDOSNode):
    type: Optional[str] = "N_TreatmentManifest"
    edges: dict[str, Optional[Edge]] = {}


class N_Inbox(PDOSNode):
    type: Optional[str] = "N_Inbox"


class AccessPackage(BaseModel):
    ciphertext: str
    dataToEncryptHash: str

class N_UserAccount(PDOSNode):
    type: Optional[str] = "N_UserAccount"
    is_root: bool = True

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

        if expectedEdges is not None:
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
    node: dict[str, type[PDOSNode]] ={
        "N_Inbox": N_Inbox,

        "N_UserAccount": N_UserAccount,

        "N_DataManifest": N_DataManifest,
        "N_DataGroup_I": N_DataGroup_I,


        "N_TreatmentManifest": N_TreatmentManifest,
        "N_Treatment_I": N_Treatment_I,
        "N_TreatmentInstance_I": N_TreatmentInstance_I,
        "N_TreatmentBinary": N_TreatmentBinary,
        "N_TreatmentProgress": N_TreatmentProgress,
    }


    def getName(name):
        name.split("_")[1]

NetworkMapper = NetworkMapperClass()
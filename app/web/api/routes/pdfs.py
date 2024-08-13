import json
from typing import Dict, List, Optional, TypeAlias
from fastapi import APIRouter
import os
from datetime import datetime
from app.services.pdfs.pdfs import get_node_from_pdfs, add_node_to_pdfs
from app.services.pdfs.model import Edge, NetworkMapper, PDFSNode
from pydantic import BaseModel,  create_model
from app.services.pdfs import ipfs
from typing import Generic, TypeVar, Type
from pydantic.generics import GenericModel


router = APIRouter()


@router.get("/pdos")
def get_node_from_pdos(
    hash: str,
):
    assert hash is not None, "No hash id passed"
    return get_node_from_pdfs(hash).json()



class NewPDFSNodeRequest(BaseModel):
    new_node_type: Optional[str] = None
    new_node_data: str 
    new_node_instance: Optional[str] = None

    tree_path: Optional[List[str]] = []

# Define a type variable
T = TypeVar('T')

# Generic model
class NewPDFSNodeResponse(GenericModel, Generic[T]):
    new_node: T
    new_tree_path: List[str]
    old_tree_path: List[str]


def get_core_node_type(node_type: str):
    node_split = node_type.split("_") 

    if (len(node_split) >= 3):
        return node_split[0] + "_" + node_split[1] + "_I"
    else:
        return node_split[0] + "_" + node_split[1]

def get_node_name(node_type: str):
    node_split = node_type.split("_") 
    if (len(node_split) >= 3):
        return node_split[1] + "_" + node_split[2]
    else:
        return node_split[1]

def get_node_instance_type(node_type: str):
    node_split = node_type.split("_") 
    if (len(node_split) == 3):
        return node_split[2]
    else:
        return None


def is_instance_node(node_type: str):
    node_split = node_type.split("_") 
    return len(node_split) == 3


@router.post("/pdos")
def add_node_to_pdos(
    new_pdfs_node: NewPDFSNodeRequest
) -> NewPDFSNodeResponse:
    core_node_type = get_core_node_type(new_pdfs_node.new_node_type) 
    new_node_data_json = json.loads(new_pdfs_node.new_node_data)
    data_model = NetworkMapper.node[core_node_type](**new_node_data_json)
    print("data_model", data_model)

    if is_instance_node(new_pdfs_node.new_node_type):
        data_model.init_instance(get_node_instance_type(new_pdfs_node.new_node_type)) 

    newly_added_pdfs_node = add_node_to_pdfs(
        data_model,
    )

    new_tree_path = []
    new_tree_path.append(newly_added_pdfs_node.hash_id)

    def update_parent_nodes(parent_node_hash_list: List[str], new_node: PDFSNode) -> PDFSNode:

        next_parent_hash = parent_node_hash_list.pop()

        parent_node = get_node_from_pdfs(next_parent_hash)
        node_name = get_node_name(new_node.type)

        relation_to_child = 'e_out_' + node_name

        updated_parent_node = parent_node.copy()
        updated_parent_node.edges[relation_to_child] = Edge(
            type=new_node.type,
            child_hash_id=new_node.hash_id
        ) 

        new_parent_node = add_node_to_pdfs(
            updated_parent_node,
        )

        new_tree_path.append(new_parent_node.hash_id)
        if parent_node.is_root:
            if (parent_node.type == "N_UserAccount"):
                alpine = ipfs.ALPINE_NODE_MANIFEST 
                updated_alpine = alpine.copy()

                if (parent_node.hash_id in updated_alpine.users):
                    del updated_alpine.users[parent_node.hash_id]

                updated_alpine.users[new_parent_node.hash_id] = True
                ipfs.update_alpine_node_manifest(updated_alpine)
        else:
            update_parent_nodes(parent_node_hash_list, new_parent_node)


    if len(new_pdfs_node.tree_path) > 0:
        update_parent_nodes(new_pdfs_node.tree_path, newly_added_pdfs_node)

    return NewPDFSNodeResponse[NetworkMapper.node[core_node_type]](
        new_node=newly_added_pdfs_node,
        new_tree_path = list(reversed(new_tree_path)),
        old_tree_path = new_pdfs_node.tree_path
    )

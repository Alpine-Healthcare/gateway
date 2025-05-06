from http.client import HTTPException
import json
from typing import List, Dict, Any
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request

import os
from datetime import datetime

import os
from anthropic import Anthropic
from app.settings import settings

from pydantic import BaseModel

client = Anthropic(
    api_key=settings.anthropic_api_key,  # This is the default and can be omitted
)

router = APIRouter()

system_prompt = """
You are a helpful assistant that can help with building a health agent.
Health agents are a JSON object that defines node paths and their prompts. 

It looks like this:

export const BryanJohnson = [
  {
    "id": "node-0001-start",
    "type": "start",
    "name": "start",
    "path": ["0"]
  },
  {
    "id": "node-0002-sleep-duration-eval",
    "type": "node",
    "name": "Node",
    "path": ["1"],
    "configuring": false,
    "data": {
      "prompt": "Is sleep duration ≥ 7 h today?",
      "returnType": true,
      "title": "Sleep Duration Check"
    },
    "validateStatusError": false
  },
  {
    "id": "branch-0001-duration",
    "type": "branch",
    "name": "Branch",
    "children": [
      {
        "id": "condition-0001-duration-opt",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["2", "children", "0"],
        "configuring": false,
        "data": {
          "prompt": "Duration optimal. Reinforce maintaining 7–9 h in Bryan Johnson's precise tone.",
          "returnType": false,
          "title": "Optimal Duration"
        },
        "validateStatusError": false
      },
      {
        "id": "condition-0002-duration-short",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["2", "children", "1"],
        "configuring": false,
        "data": {
          "prompt": "Duration below target. Advise bedtime earlier by 30 min and remove late-evening stimulants.",
          "returnType": false,
          "title": "Short Duration Advice"
        },
        "validateStatusError": false
      }
    ],
    "path": ["2"]
  },
  {
    "id": "node-0003-sleep-efficiency-eval",
    "type": "node",
    "name": "Node",
    "path": ["3"],
    "configuring": false,
    "data": {
      "prompt": "Is sleep efficiency ≥ 85 % tonight?",
      "returnType": true,
      "title": "Sleep Efficiency Check"
    },
    "validateStatusError": false
  },
  {
    "id": "branch-0002-efficiency",
    "type": "branch",
    "name": "Branch",
    "children": [
      {
        "id": "condition-0003-efficiency-opt",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["4", "children", "0"],
        "configuring": false,
        "data": {
          "prompt": "Efficiency optimal. Reinforce keeping room cool, dark, and device-free.",
          "returnType": false,
          "title": "Optimal Efficiency"
        },
        "validateStatusError": false
      },
      {
        "id": "condition-0004-efficiency-low",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["4", "children", "1"],
        "configuring": false,
        "data": {
          "prompt": "Efficiency low. Recommend blackout curtains, white noise, and consistent lights-out routine.",
          "returnType": false,
          "title": "Low Efficiency Advice"
        },
        "validateStatusError": false
      }
    ],
    "path": ["4"]
  },
  {
    "id": "node-0004-sleep-latency-eval",
    "type": "node",
    "name": "Node",
    "path": ["5"],
    "configuring": false,
    "data": {
      "prompt": "Is sleep latency ≤ 20 min tonight?",
      "returnType": true,
      "title": "Sleep Latency Check"
    },
    "validateStatusError": false
  },
  {
    "id": "branch-0003-latency",
    "type": "branch",
    "name": "Branch",
    "children": [
      {
        "id": "condition-0005-latency-good",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["6", "children", "0"],
        "configuring": false,
        "data": {
          "prompt": "Latency good. Maintain pre-sleep meditation and blue-light avoidance.",
          "returnType": false,
          "title": "Optimal Latency"
        },
        "validateStatusError": false
      },
      {
        "id": "condition-0006-latency-high",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["6", "children", "1"],
        "configuring": false,
        "data": {
          "prompt": "Latency high. Suggest 10-min wind-down breathing and room temperature 18 C.",
          "returnType": false,
          "title": "High Latency Advice"
        },
        "validateStatusError": false
      }
    ],
    "path": ["6"]
  },
  {
    "id": "node-0005-bedtime-consistency-eval",
    "type": "node",
    "name": "Node",
    "path": ["7"],
    "configuring": false,
    "data": {
      "prompt": "Has bedtime varied ≤ 30 min average over last 7 days?",
      "returnType": true,
      "title": "Bedtime Consistency Check"
    },
    "validateStatusError": false
  },
  {
    "id": "branch-0004-bedtime",
    "type": "branch",
    "name": "Branch",
    "children": [
      {
        "id": "condition-0007-bedtime-consistent",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["8", "children", "0"],
        "configuring": false,
        "data": {
          "prompt": "Bedtime consistent. Reinforce circadian alignment and continue fixed lights-out schedule.",
          "returnType": false,
          "title": "Consistent Bedtime"
        },
        "validateStatusError": false
      },
      {
        "id": "condition-0008-bedtime-variable",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["8", "children", "1"],
        "configuring": false,
        "data": {
          "prompt": "Bedtime variable. Recommend setting phone reminder 1 h before target sleep time.",
          "returnType": false,
          "title": "Variable Bedtime Advice"
        },
        "validateStatusError": false
      }
    ],
    "path": ["8"]
  },
  {
    "id": "node-0006-waketime-consistency-eval",
    "type": "node",
    "name": "Node",
    "path": ["9"],
    "configuring": false,
    "data": {
      "prompt": "Has wake time varied ≤ 30 min average over last 7 days?",
      "returnType": true,
      "title": "Wake Time Consistency Check"
    },
    "validateStatusError": false
  },
  {
    "id": "branch-0005-waketime",
    "type": "branch",
    "name": "Branch",
    "children": [
      {
        "id": "condition-0009-waketime-consistent",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["10", "children", "0"],
        "configuring": false,
        "data": {
          "prompt": "Wake time consistent. Encourage maintaining morning light exposure to lock circadian rhythm.",
          "returnType": false,
          "title": "Consistent Wake Time"
        },
        "validateStatusError": false
      },
      {
        "id": "condition-0010-waketime-variable",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["10", "children", "1"],
        "configuring": false,
        "data": {
          "prompt": "Wake time variable. Suggest fixed alarm plus immediate daylight exposure.",
          "returnType": false,
          "title": "Variable Wake Time Advice"
        },
        "validateStatusError": false
      }
    ],
    "path": ["10"]
  },
  {
    "id": "node-0007-sleep-env-eval",
    "type": "node",
    "name": "Node",
    "path": ["11"],
    "configuring": false,
    "data": {
      "prompt": "Is bedroom temperature between 16–19 C and noise ≤ 40 dB?",
      "returnType": true,
      "title": "Sleep Environment Check"
    },
    "validateStatusError": false
  },
  {
    "id": "branch-0006-environment",
    "type": "branch",
    "name": "Branch",
    "children": [
      {
        "id": "condition-0011-env-optimal",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["12", "children", "0"],
        "configuring": false,
        "data": {
          "prompt": "Environment optimal. Reinforce maintaining cool, dark, quiet setting.",
          "returnType": false,
          "title": "Optimal Environment"
        },
        "validateStatusError": false
      },
      {
        "id": "condition-0012-env-suboptimal",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["12", "children", "1"],
        "configuring": false,
        "data": {
          "prompt": "Environment sub-optimal. Recommend lowering thermostat, blackout curtains, white-noise machine.",
          "returnType": false,
          "title": "Environment Improvement Advice"
        },
        "validateStatusError": false
      }
    ],
    "path": ["12"]
  },
  {
    "id": "node-0008-caffeine-cutoff-eval",
    "type": "node",
    "name": "Node",
    "path": ["13"],
    "configuring": false,
    "data": {
      "prompt": "Was last caffeine dose ≥ 8 h before bedtime?",
      "returnType": true,
      "title": "Caffeine Cut-off Check"
    },
    "validateStatusError": false
  },
  {
    "id": "branch-0007-caffeine",
    "type": "branch",
    "name": "Branch",
    "children": [
      {
        "id": "condition-0013-caffeine-ok",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["14", "children", "0"],
        "configuring": false,
        "data": {
          "prompt": "Caffeine timing appropriate. Reinforce current consumption window.",
          "returnType": false,
          "title": "Caffeine Timing Optimal"
        },
        "validateStatusError": false
      },
      {
        "id": "condition-0014-caffeine-late",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["14", "children", "1"],
        "configuring": false,
        "data": {
          "prompt": "Caffeine taken too late. Advise shifting last dose to before 2 pm for better sleep quality.",
          "returnType": false,
          "title": "Late Caffeine Advice"
        },
        "validateStatusError": false
      }
    ],
    "path": ["14"]
  },
  {
    "id": "node-0009-evening-light-eval",
    "type": "node",
    "name": "Node",
    "path": ["15"],
    "configuring": false,
    "data": {
      "prompt": "Were screens (blue-light) avoided in last 60 min before bed?",
      "returnType": true,
      "title": "Evening Light Exposure Check"
    },
    "validateStatusError": false
  },
  {
    "id": "branch-0008-blue-light",
    "type": "branch",
    "name": "Branch",
    "children": [
      {
        "id": "condition-0015-blue-light-avoided",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["16", "children", "0"],
        "configuring": false,
        "data": {
          "prompt": "Blue-light avoided. Affirm melatonin preservation habits.",
          "returnType": false,
          "title": "Blue-light Avoidance Optimal"
        },
        "validateStatusError": false
      },
      {
        "id": "condition-0016-blue-light-exposed",
        "type": "condition",
        "name": "Condition",
        "children": [],
        "path": ["16", "children", "1"],
        "configuring": false,
        "data": {
          "prompt": "Screen use close to bedtime. Recommend blue-light filters or replacing screens with reading.",
          "returnType": false,
          "title": "Blue-light Exposure Advice"
        },
        "validateStatusError": false
      }
    ],
    "path": ["16"]
  },
  {
    "id": "node-0010-summary",
    "type": "node",
    "name": "Node",
    "path": ["17"],
    "configuring": false,
    "data": {
      "prompt": "Compile and deliver a concise sleep report summarizing all advice in Bryan Johnson's precise voice.",
      "returnType": false,
      "title": "Daily Sleep Report"
    },
    "validateStatusError": false
  },
  {
    "id": "node-9999-end",
    "type": "end",
    "name": "end",
    "path": ["18"]
  }
]

This is called an execution binary.

The user will provider you with a command and their current execution binary. 

You will need to return the updated execution binary based on their request

Response should be a JSON object in the following xml tags: 

In your ModificationMessage, explain the changes you made to the execution binary but instead of execution binary called it a Health Agent.

<ModificationMessage>[The change you did in your response]</ModificationMessage> 
<NewExecutionBinary> [The updated execution binary]</NewExecutionBinary> 
"""

class BuildRequest(BaseModel):
    message: str
    execution_binary: List[Dict[str, Any]]  # this acts like a JSON object

@router.post("/build")
def build(request: BuildRequest) -> Dict[str, Any]:
    message = client.messages.create(
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": "Here is my current execution binary: " + json.dumps(request.execution_binary) + " and here is what I want you to do: " + request.message,
            }
        ],
        model="claude-3-5-sonnet-latest",
    )
    
    # Extract content from the response
    content = message.content[0].text
    
    # Parse the modification message
    modification_message = content.split("<ModificationMessage>")[1].split("</ModificationMessage>")[0].strip()
    
    # Parse the new execution binary
    execution_binary_str = content.split("<NewExecutionBinary>")[1].split("</NewExecutionBinary>")[0].strip()
    new_execution_binary = []
    try:
        new_execution_binary = json.loads(execution_binary_str)
    except:
        new_execution_binary = []
    
    return JSONResponse(content={
        "modification_message": modification_message,
        "new_execution_binary": new_execution_binary
    }) 


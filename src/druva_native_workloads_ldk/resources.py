"""A module containing the langchain tool for Druva Native Workloads resources"""

import os
import json
import base64
from typing import Optional, Type

import requests
from aiohttp import ClientSession
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

DRUVA_NATIVE_WORKLOADS_API_URL = "https://api.cloudranger.com/202004"

class DruvaNativeWorkloadsResourcesInput(BaseModel):
    """Structure for resources tool input"""
    account_id: Optional[str] = Field(description="account_id, required attribute, can be retrieved using the accounts tool")
    organization_id: Optional[str] = Field(description="organization_id, can be left empty if unclear")

class DruvaNativeWorkloadsResourcesTool(BaseTool):
    """A langchain tool to retrieve Druva Native Workloads Resources"""
    name = "get_druva_native_workloads_resources"
    description = (
        "useful for getting druva native workloads "
        "resources information for a specific organization "
        "in JSON format"
    )
    args_schema: Type[BaseModel] = DruvaNativeWorkloadsResourcesInput

    async def _arun(
        self,
        account_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> str:
        """Run the tool async"""
        async with ClientSession() as session:

            # Validate API key
            api_key = os.environ.get('DRUVA_NATIVE_WORKLOADS_API_KEY')
            if api_key is None:
                raise ValueError(
                    "Did not find DRUVA_NATIVE_WORKLOADS_API_KEY"
                    ", please add it as an environment variable"
                )

            # Obtain a valid JWT
            async with session.get(
                f"{DRUVA_NATIVE_WORKLOADS_API_URL}/authorize",
                headers={"x-api-key": api_key},
            ) as authorize_result:
                authorize_result = await authorize_result.json()
                jwt = authorize_result['token']
                jwt_payload = jwt.split('.')[1].encode('ascii') + b'=='
                b64decoded_jwt = base64.b64decode(jwt_payload).decode('ascii')
                decoded_jwt = json.loads(b64decoded_jwt)

                # Populate organization_id with first ID available if it wasn't passed
                if organization_id is None or organization_id == "":
                    organization_id = list(decoded_jwt['app_metadata']['organizations'].keys())[0]
                if account_id is None or account_id == "":
                    return "An account_id parameter is required"
                async with session.get(
                    (
                        f"{DRUVA_NATIVE_WORKLOADS_API_URL}/organizations/"
                        f"{organization_id}/accounts/{account_id}/resources?pageSize=10"
                    ),
                    headers={
                        "authorization": f"Bearer {jwt}",
                        "x-api-key": api_key,
                    },
                ) as result:
                    result = await result.json()
                    return json.dumps(result["hits"])


    def _run(
        self,
        account_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> str:
        """Run the tool"""
        # Validate API key
        api_key = os.environ.get('DRUVA_NATIVE_WORKLOADS_API_KEY')
        if api_key is None:
            raise ValueError(
                "Did not find DRUVA_NATIVE_WORKLOADS_API_KEY, "
                "please add it as an environment variable"
            )

        # Obtain a valid JWT
        authorize_result = requests.get(
            f"{DRUVA_NATIVE_WORKLOADS_API_URL}/authorize",
            headers={"x-api-key": api_key},
            timeout=5,
        ).json()
        jwt = authorize_result['token']
        jwt_payload = jwt.split('.')[1].encode('ascii') + b'=='
        b64decoded_jwt = base64.b64decode(jwt_payload).decode('ascii')
        decoded_jwt = json.loads(b64decoded_jwt)
        # Populate organization_id with first ID available if it wasn't passed
        if organization_id is None or organization_id == "":
            organization_id = list(decoded_jwt['app_metadata']['organizations'].keys())[0]
        if account_id is None or account_id == '':
            return "An account_id parameter is required"
        result = requests.get(
            (
                f"{DRUVA_NATIVE_WORKLOADS_API_URL}/organizations/"
                f"{organization_id}/accounts/{account_id}/resources?pageSize=10"
            ),
            headers={
                "authorization": f"Bearer {jwt}",
                "x-api-key": api_key,
            },
            timeout=5,
        ).json()
        return json.dumps(result["hits"])

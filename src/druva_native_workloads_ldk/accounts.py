"""A module containing the langchain tool for Druva Native Workloads accounts"""

import os
import json
import base64
from typing import Optional, Type

import requests
from aiohttp import ClientSession
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

DRUVA_NATIVE_WORKLOADS_API_URL = "https://api.cloudranger.com/202004"

class DruvaNativeWorkloadsAccountsInput(BaseModel):
    """Structure for accounts tool input"""
    organization_id: Optional[str] = Field(description="organization_id, can be left empty if unclear")

class DruvaNativeWorkloadsAccountsTool(BaseTool):
    """A langchain tool to retrieve Druva Native Workloads Accounts"""
    name = "get_druva_native_workloads_accounts"
    description = (
        "useful for getting druva native workloads "
        "accounts information for a specific organization "
        "in JSON format"
    )
    args_schema: Type[BaseModel] = DruvaNativeWorkloadsAccountsInput

    async def _arun(
        self,
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

                async with session.get(
                    (
                        f"{DRUVA_NATIVE_WORKLOADS_API_URL}"
                        f"/organizations/{organization_id}/accounts?lite=true"
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

        result = requests.get(
            (
                f"{DRUVA_NATIVE_WORKLOADS_API_URL}/organizations/"
                f"{organization_id}/accounts?lite=true"
            ),
            headers={
                "authorization": f"Bearer {jwt}",
                "x-api-key": api_key,
            },
            timeout=5,
        ).json()
        return json.dumps(result["hits"])

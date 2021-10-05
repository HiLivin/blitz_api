from app.auth.auth_bearer import JWTBearer
from app.models.bitcoind import BlockchainInfo, BtcInfo, NetworkInfo
from app.repositories.bitcoin import (
    get_blockchain_info,
    get_btc_info,
    get_network_info,
    handle_block_sub,
)
from app.routers.bitcoin_docs import blocks_sub_doc
from app.sse_starlette import EventSourceResponse
from app.utils import bitcoin_rpc
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.params import Depends

_PREFIX = "bitcoin"

router = APIRouter(prefix=f"/{_PREFIX}", tags=["Bitcoin Core"])


@router.get(
    "/btc-info",
    name=f"{_PREFIX}.btc-info",
    description="Get general information about bitcoin core. Combines most important information from `getblockchaininfo` and `getnetworkinfo`",
    dependencies=[Depends(JWTBearer())],
    response_model=BtcInfo,
)
async def btc_info_path():
    return await get_btc_info()


@router.get(
    "/get-block-count",
    name=f"{_PREFIX}.get-block-count",
    summary="Get the current block count",
    description="See documentation on [bitcoincore.org](https://bitcoincore.org/en/doc/0.21.0/rpc/blockchain/getblockcount/)",
    response_description="""A JSON String with relevant information.\n
```json
{
  \"result\": 682621,
  \"error\": null,
  \"id\": 0
}
""",
    dependencies=[Depends(JWTBearer())],
)
def getblockcount():
    r = bitcoin_rpc("getblockcount")

    if r.status_code == status.HTTP_200_OK:
        return r.content
    else:
        raise HTTPException(r.status_code, detail=r.reason)


@router.get(
    "/get-blockchain-info",
    name=f"{_PREFIX}.get-blockchain-info",
    summary="Get the current blockchain status",
    description="See documentation on [bitcoincore.org](https://bitcoincore.org/en/doc/0.21.0/rpc/blockchain/getblockchaininfo/)",
    response_description="A JSON String with relevant information.",
    dependencies=[Depends(JWTBearer())],
    response_model=BlockchainInfo,
)
async def getblockchaininfo():
    info = await get_blockchain_info()
    return info


@router.get(
    "/get-network-info",
    name=f"{_PREFIX}.get-network-info",
    summary="Get information about the network",
    description="See documentation on [bitcoincore.org](https://bitcoincore.org/en/doc/0.21.0/rpc/network/getnetworkinfo/)",
    response_description="A JSON String with relevant information.",
    dependencies=[Depends(JWTBearer())],
    status_code=status.HTTP_200_OK,
    response_model=NetworkInfo,
)
async def getnetworkinfo():
    info = await get_network_info()
    return info


@router.get(
    "/block-sub",
    name=f"{_PREFIX}.block-sub",
    summary="Subscribe to incoming blocks.",
    description=blocks_sub_doc,
    response_description="A JSON object with information about the new block.",
    dependencies=[Depends(JWTBearer())],
)
async def zmq_sub(request: Request, verbosity: int = 1):
    return EventSourceResponse(handle_block_sub(request, verbosity))

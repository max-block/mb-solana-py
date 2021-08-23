from typing import Any, Optional

from mb_commons import Result, hrequest


def rpc_call(*, node: str, method: str, params: list[Any], id_=1, timeout=10, proxy=None) -> Result:
    data = {"jsonrpc": "2.0", "method": method, "params": params, "id": id_}
    if node.startswith("http"):
        return _http_call(node, data, timeout, proxy)
    else:
        raise NotImplementedError("ws is not implemented")


def _http_call(node: str, data: dict, timeout: int, proxy: Optional[str]) -> Result:
    res = hrequest(node, method="POST", proxy=proxy, timeout=timeout, params=data, json_params=True)
    try:
        if res.is_error():
            return res.to_error()

        err = res.json.get("error", {}).get("message", "")
        if err:
            return res.to_error(f"service_error: {err}")
        if "result" in res.json:
            return res.to_ok(res.json["result"])

        return res.to_error("unknown_response")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def _remove_me_get_inflation_reward(
    node: str,
    address: str,
    epoch: Optional[int] = None,
    timeout=10,
    proxy=None,
) -> Result[int]:
    """Returns reward in lamports"""
    params: list[Any] = [[address]]
    if epoch:
        params.append({"epoch": epoch})
    res = rpc_call(node=node, method="getInflationReward", params=params, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    try:
        res.ok = res.ok[0]["amount"]
        return res
    except Exception as e:
        return Result(error=f"exception: {str(e)}", data=res.dict())


def get_balance(node: str, address: str, timeout=10, proxy=None) -> Result[int]:
    """Returns balance in lamports"""
    params = [address]
    res = rpc_call(node=node, method="getBalance", params=params, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res
    try:
        res.ok = res.ok["value"]
        return res
    except Exception as e:
        return Result(error=f"exception: {str(e)}", data=res.dict())


if __name__ == "__main__":
    pass

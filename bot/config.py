import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import TypedDict

from tinybot import multicall
from web3 import Web3


class NetworkCfg(TypedDict):
    registry: str
    factory: str
    explorer: str
    known_addresses: dict[str, str]


NETWORKS: Mapping[str, NetworkCfg] = {
    "ethereum": {
        "registry": "0x9117440a7D03238905d1C8908157Bd7a547c77c8",
        "factory": "0xe2c4a5C2AB1ed5745D206B33cc0abf0A5D34753d",
        "explorer": "https://etherscan.io/",
        "known_addresses": {
            "0xEf77cc176c748d291EfB6CdC982c5744fC7211c8": "yRoboTreasury",
            "0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7": "SMS",
            "0x9008D19f58AAbD9eD0D60971565AA8510560ab41": "Mooo 🐮",
            "0x1DA3902C196446dF28a2b02Bf733cA31A00A161b": "TradeHandler",
            "0x84483314d2AD44Aa96839F048193CE9750AA66B0": "gekko",
            "0x5CECc042b2A320937c04980148Fc2a4b66Da0fbF": "gekko",
            "0xb911Fcce8D5AFCEc73E072653107260bb23C1eE8": "Yearn veCRV Fee Burner",
            "0xE08D97e151473A848C3d9CA3f323Cb720472D015": "c0ffeebabe.eth",
            "0x5b6046ca3b7EA44Eb016757C2E6A7ecc41273ca3": "piggy",
        },
    },
}

# Common Report Trigger and Permissionless Keeper (Yearn V3)
COMMON_REPORT_TRIGGER = Web3.to_checksum_address("0xf8dF17a35c88AbB25e83C92f9D293B4368b9D52D")
PERMISSIONLESS_KEEPER = Web3.to_checksum_address("0x52605BbF54845f520a3E94792d019f62407db2f8")

# Intervals
INTERVAL = 300
REPORT_INTERVAL = 3600

# Max base fee for reporting (gwei)
MAX_GAS_GWEI = 1

# Alerts
ALERTS_STATE_PATH = os.environ.get("ALERTS_STATE_PATH", "alerts.json")
MAX_ADDRESSES_PER_USER = 5

# Alerts backup (private GitHub repo, via the Contents API)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")  # "owner/repo"
GITHUB_BACKUP_PATH = "alerts.json"
GITHUB_BACKUP_BRANCH = "main"
BACKUP_INTERVAL = 86400

# ABIs
_abis = Path(__file__).parent / "abis"
REGISTRY_ABI = json.loads((_abis / "registry.json").read_text())
FACTORY_ABI = json.loads((_abis / "factory.json").read_text())
TROVE_MANAGER_ABI = json.loads((_abis / "trove_manager.json").read_text())
DUTCH_DESK_ABI = json.loads((_abis / "dutch_desk.json").read_text())
AUCTION_ABI = json.loads((_abis / "auction.json").read_text())
LENDER_ABI = json.loads((_abis / "lender.json").read_text())
REPORT_TRIGGER_ABI = json.loads((_abis / "report_trigger.json").read_text())
KEEPER_ABI = json.loads((_abis / "keeper.json").read_text())
ERC20_ABI = json.loads((_abis / "erc20.json").read_text())


def network() -> str:
    return os.environ.get("NETWORK", "ethereum")


def cfg() -> NetworkCfg:
    return NETWORKS[network()]


def explorer_tx_url() -> str:
    return cfg()["explorer"] + "tx/"


def fmt(val: float, decimals: int = 2) -> str:
    """Format with thousand separators; strip decimals if all zeros."""
    s = f"{val:,.{decimals}f}"
    if s.endswith("." + "0" * decimals):
        return s[: -(decimals + 1)]
    return s


def short(val: str) -> str:
    """Shorten an address or ID to first 6 and last 4 chars."""
    val = str(val)
    if len(val) <= 10:
        return val
    return f"{val[:6]}...{val[-4:]}"


def parse_address(raw: str) -> str | None:
    """Return the checksummed address, or None if invalid."""
    try:
        return Web3.to_checksum_address(raw.strip())
    except (ValueError, TypeError):
        return None


def safe_name(w3: Web3, address: str, shorten: bool = False) -> str:
    address = w3.to_checksum_address(address)
    try:
        c = w3.eth.contract(address=address, abi=ERC20_ABI)
        return c.functions.name().call()
    except Exception:
        pass
    try:
        name = w3.ens.name(address)
        if name:
            return str(name)
    except Exception:
        pass
    known = cfg()["known_addresses"].get(address)
    if known:
        return known
    return short(address) if shorten else address


def labeled_address(w3: Web3, address: str) -> str:
    """Address as tap-to-copy <code>, prefixed with its name if one resolves."""
    address = Web3.to_checksum_address(address)
    name = safe_name(w3, address)
    if name == address:
        return f"<code>{address}</code>"
    return f"{name} (<code>{address}</code>)"


def registry_addr() -> str:
    return Web3.to_checksum_address(cfg()["registry"])


def factory_addr() -> str:
    return Web3.to_checksum_address(cfg()["factory"])


def get_all_markets(w3: Web3) -> list[str]:
    """Get all endorsed trove manager addresses from the registry."""
    registry = w3.eth.contract(address=registry_addr(), abi=REGISTRY_ABI)
    markets: list[str] = registry.functions.get_all_markets().call()

    # Filter to only endorsed markets (Status.ENDORSED = 1)
    status_calls = [registry.functions.market_status(w3.to_checksum_address(m)) for m in markets]
    statuses = multicall(w3, status_calls)
    return [w3.to_checksum_address(m) for m, s in zip(markets, statuses) if s == 1]


def get_all_lenders(w3: Web3, markets: list[str]) -> list[str]:
    """Get lender addresses for all trove managers."""
    lender_calls = [
        w3.eth.contract(address=w3.to_checksum_address(m), abi=TROVE_MANAGER_ABI).functions.lender() for m in markets
    ]
    lenders = multicall(w3, lender_calls)
    return list(set(w3.to_checksum_address(addr) for addr in lenders))


def get_all_auctions(w3: Web3, markets: list[str]) -> list[str]:
    """Get all auction contract addresses from markets."""
    dutch_desk_calls = [
        w3.eth.contract(address=w3.to_checksum_address(m), abi=TROVE_MANAGER_ABI).functions.dutch_desk()
        for m in markets
    ]
    dutch_desks = multicall(w3, dutch_desk_calls)

    auction_calls = [
        w3.eth.contract(address=w3.to_checksum_address(dd), abi=DUTCH_DESK_ABI).functions.auction()
        for dd in dutch_desks
    ]
    auction_addrs = multicall(w3, auction_calls)
    return list(set(w3.to_checksum_address(a) for a in auction_addrs))

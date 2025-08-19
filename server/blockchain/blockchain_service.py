# blockchain_service.py : Blockchain service implementation

import json
import os
import time
import hashlib
import threading
from typing import Any, Dict, List, Tuple, Optional
from blockchain import Blockchain

# Thread-safety for concurrent reads/writes
_LOCK = threading.Lock()

# Persist ledger in the same folder as this file
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LEDGER_PATH = os.path.join(_THIS_DIR, "ledger.json")

# =======================
# Low-level helper funcs
# =======================

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _block_hash(block: Dict[str, Any]) -> str:
    """
    Deterministic hash of a block (excluding its own `hash` field).
    """
    payload = {
        "index": block["index"],
        "timestamp": block["timestamp"],
        "data": block["data"],
        "prev_hash": block["prev_hash"],
        "nonce": block.get("nonce", 0),
    }
    # Compact + sorted to guarantee stable hashing
    return _sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")))

def _genesis_block() -> Dict[str, Any]:
    """
    Deterministic genesis block. If ledger is missing/corrupt, we recreate it with this.
    """
    block = {
        "index": 0,
        "timestamp": 0.0,                # fixed timestamp for deterministic genesis
        "data": {"genesis": True},
        "prev_hash": "0" * 64,           # no parent
        "nonce": 0,
    }
    block["hash"] = _block_hash(block)
    return block

def _load_chain() -> List[Dict[str, Any]]:
    """
    Load chain from disk, auto-create if missing/corrupt/empty.
    """
    if not os.path.exists(_LEDGER_PATH):
        chain = [_genesis_block()]
        _save_chain(chain)
        return chain

    with open(_LEDGER_PATH, "r", encoding="utf-8") as f:
        try:
            chain = json.load(f)
        except json.JSONDecodeError:
            chain = [_genesis_block()]

    if not isinstance(chain, list) or len(chain) == 0:
        chain = [_genesis_block()]

    # Ensure genesis is correct
    if chain[0] != _genesis_block():
        chain = [_genesis_block()]

    return chain

def _save_chain(chain: List[Dict[str, Any]]) -> None:
    """
    Atomic write to avoid partial/corrupt files on crash.
    """
    tmp = _LEDGER_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(chain, f, indent=2)
    os.replace(tmp, _LEDGER_PATH)

# =======================
# Public API
# =======================

def get_chain() -> List[Dict[str, Any]]:
    """
    Return a *copy* of the full chain to avoid accidental external mutation.
    """
    with _LOCK:
        chain = _load_chain()
        # Return a shallow copy (blocks are dicts; callers should treat as read-only)
        return list(chain)

def get_last_block() -> Dict[str, Any]:
    """
    Get the most recent block.
    """
    with _LOCK:
        chain = _load_chain()
        return chain[-1]

def add_block(data: Dict[str, Any], *, difficulty: int = 0) -> Dict[str, Any]:
    """
    Append a new block with `data` to the chain.

    Args:
        data: dict payload you want to store (e.g., firewall event, rule change, etc.)
        difficulty: integer number of leading '0' bits (naive PoW). 0 disables PoW.

    Returns:
        The newly added block (dict).
    """
    if not isinstance(data, dict):
        raise ValueError("Block `data` must be a dict.")

    with _LOCK:
        chain = _load_chain()
        last = chain[-1]

        block: Dict[str, Any] = {
            "index": last["index"] + 1,
            "timestamp": time.time(),
            "data": data,
            "prev_hash": last["hash"],
            "nonce": 0,
        }

        # Optional, tiny proof-of-work for demo purposes
        prefix = "0" * int(max(0, difficulty))
        while True:
            h = _block_hash(block)
            if prefix and not h.startswith(prefix):
                block["nonce"] += 1
                continue
            block["hash"] = h
            break

        chain.append(block)
        _save_chain(chain)
        return block

def verify_chain() -> Tuple[bool, Optional[str]]:
    """
    Verify entire chain integrity.

    Returns:
        (True, None) if valid, else (False, reason).
    """
    with _LOCK:
        chain = _load_chain()

    # Check genesis block
    if chain[0] != _genesis_block():
        return False, "Genesis block mismatch."

    # Check links and hashes
    for i in range(1, len(chain)):
        prev = chain[i - 1]
        curr = chain[i]

        if curr.get("prev_hash") != prev.get("hash"):
            return False, f"Broken link at index {i}: prev_hash does not match previous block hash."

        expected = _block_hash(curr)
        if curr.get("hash") != expected:
            return False, f"Hash mismatch at index {i}: expected {expected}, got {curr.get('hash')}."

    return True, None

def log_firewall_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience wrapper tailored for firewall events.

    Example `event`:
        {
            "time": "2025-08-19T02:50:10Z",
            "source": "10.0.0.5:443",
            "destination": "1.2.3.4:5050",
            "action": "allow" | "deny",
            "rule_id": 3
        }
    """
    if not isinstance(event, dict):
        raise ValueError("`event` must be a dict.")
    payload = {"type": "firewall_event", **event}
    return add_block(payload)

def reset_chain_for_dev_only() -> None:
    """
    DEV/TEST ONLY: Reset the chain to just the genesis block.
    Never call this in production.
    """
    with _LOCK:
        _save_chain([_genesis_block()])

# =======================
# CLI: quick manual test
# =======================

if __name__ == "__main__":
    print("[Blockchain] Ledger path:", _LEDGER_PATH)

    ok, reason = verify_chain()
    print("[Verify] valid:", ok, "| reason:", reason)

    print("[Add] Adding a demo block ...")
    b = add_block({"demo": True, "ts": time.time()})
    print("[Add] Added block #", b["index"], "hash:", b["hash"])

    ok, reason = verify_chain()
    print("[Verify] After add -> valid:", ok, "| reason:", reason)

    print("[Len] Chain length:", len(get_chain()))

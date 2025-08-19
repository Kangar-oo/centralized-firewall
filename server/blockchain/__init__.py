# __init__.py : Blockchain module initialization

"""
Lightweight, tamper-evident append-only ledger (mini blockchain) for audit logs.

Public API:
    add_block(data: dict) -> dict
    log_firewall_event(event: dict) -> dict
    get_chain() -> list[dict]
    get_last_block() -> dict
    verify_chain() -> tuple[bool, Optional[str]]
    reset_chain_for_dev_only() -> None
"""

from .blockchain_service import (
    add_block,
    get_chain,
    verify_chain,
    log_firewall_event,
    get_last_block,
    reset_chain_for_dev_only,
)

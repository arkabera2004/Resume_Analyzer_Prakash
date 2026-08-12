"""Shared rate limiter, keyed by client IP.

In-memory storage (slowapi's default) — fine for a single-process deployment
(this project's scope), but limits won't be shared across multiple worker
processes/instances. A Redis-backed storage would be needed for that; not
worth the added infra for a portfolio project's scale.

Applied selectively, not globally: auth endpoints (brute-force protection) and
AI endpoints (cost/abuse protection, since every call spends real API budget).
Read-heavy endpoints (history, dashboard stats) are left unlimited.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

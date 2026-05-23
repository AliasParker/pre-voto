# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
from slowapi import Limiter

from app.config import settings


def _get_remote_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(
    key_func=_get_remote_ip,
    storage_uri=settings.redis_ratelimit_url,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)

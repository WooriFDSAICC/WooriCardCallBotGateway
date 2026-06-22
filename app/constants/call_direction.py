from __future__ import annotations

from enum import Enum


class CallDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"

    def path_segment(self) -> str:
        return self.value.lower()

    def metric_label(self) -> str:
        return self.path_segment()

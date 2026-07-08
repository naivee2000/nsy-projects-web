from __future__ import annotations

from abc import ABC, abstractmethod

from car_compare.models import Listing, VehicleQuery


class SourceAdapter(ABC):
    name: str

    @abstractmethod
    def collect(self, request: VehicleQuery) -> list[Listing]:
        raise NotImplementedError

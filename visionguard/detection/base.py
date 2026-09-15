"""
Base detection structures and interfaces.
"""

from dataclasses import dataclass
from typing import Tuple, List
from abc import ABC, abstractmethod
import numpy as np


@dataclass
class Detection:
    """Represents a single detected object in a frame."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    class_id: int
    class_name: str

    @property
    def centroid(self) -> Tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]

    @property
    def area(self) -> int:
        return self.width * self.height


class BaseDetector(ABC):
    """Abstract detector interface for swap-and-play AI model backends."""

    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Process a BGR numpy frame and return detected targets."""
        pass

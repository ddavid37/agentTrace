"""Security detection approaches. Only a simple baseline is implemented today."""

from agenttrace.detection.base import CompositeDetector, Detector
from agenttrace.detection.baseline import BaselineRuleDetector

__all__ = ["BaselineRuleDetector", "CompositeDetector", "Detector"]

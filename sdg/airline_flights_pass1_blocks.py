"""Load airline pass-1 generator blocks from the sdg_hub workspace copy."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_SOURCE_BLOCKS_PATH = (
    Path(__file__).resolve().parents[2]
    / "sdg_hub"
    / "testing-claude-skills-for-sdg"
    / "airline_flights_pass1_blocks.py"
)

_SPEC = spec_from_file_location("_sdg_airline_pass1_blocks", _SOURCE_BLOCKS_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Could not load module spec from {_SOURCE_BLOCKS_PATH}")

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

AirlineFlightLongGeneratorBlock = _MODULE.AirlineFlightLongGeneratorBlock
AirlineFlightsObjectBuilderBlock = _MODULE.AirlineFlightsObjectBuilderBlock

__all__ = [
    "AirlineFlightLongGeneratorBlock",
    "AirlineFlightsObjectBuilderBlock",
]

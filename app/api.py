from fastapi import FastAPI
from pydantic import BaseModel

from .config import load_settings
from .logging_config import setup_logging
from .config.settings import Settings
from .main import execute_pipeline

# Load base settings and configure logging once at startup
_base_settings: Settings = load_settings()
setup_logging(_base_settings)

app = FastAPI(
    title="BIG Pipeline API",
    description="Agentic pipeline to generate general context, ideal roles, and actionable brief.",
    version="1.0.0",
)


class RunRequest(BaseModel):
    axis_of_exploration: str
    unit_of_analysis: str
    ideal_roles: int | None = None
    external_research: bool | None = None
    constraints: str | None = None
    complex_unit: bool | None = None
    country: str | None = None


class RunResponse(BaseModel):
    run_dir: str
    step1_general_context: str
    step2_ideal_roles_prompt: str
    step3_actionable_context_brief: str


@app.post("/run", response_model=RunResponse)
async def run_pipeline_endpoint(req: RunRequest) -> RunResponse:
    """
    Execute the BIG pipeline for a given Axis of Exploration and Unit of Analysis.

    This endpoint:
      - Overrides the base settings with request-specific values
      - Runs the 3-step pipeline (context → roles → actionable brief)
      - Persists artefacts on disk in a per-run folder
      - Returns all three textual outputs + run directory path
    """
    # Start from base settings loaded from .env, then override
    update = {
        "AXIS_OF_EXPLORATION": req.axis_of_exploration,
        "UNIT_OF_ANALYSIS": req.unit_of_analysis,
    }

    if req.ideal_roles is not None:
        update["IDEAL_ROLES"] = req.ideal_roles
    if req.external_research is not None:
        update["EXTERNAL_RESEARCH"] = req.external_research
    if req.constraints is not None:
        update["CONSTRAINTS"] = req.constraints
    if req.complex_unit is not None:
        update["COMPLEX_UNIT"] = req.complex_unit
    if req.country is not None:
        update["COUNTRY"] = req.country

    settings_for_run = _base_settings.model_copy(update=update)

    result = execute_pipeline(settings_for_run, emit_console=False)

    return RunResponse(
        run_dir=result["run_dir"],
        step1_general_context=result["step1_general_context"],
        step2_ideal_roles_prompt=result["step2_ideal_roles_prompt"],
        step3_actionable_context_brief=result["step3_actionable_context_brief"],
    )

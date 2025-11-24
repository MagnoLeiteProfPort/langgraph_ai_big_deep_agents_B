import logging
import re
from datetime import datetime
from pathlib import Path

from .config import load_settings
from .logging_config import setup_logging
from .config.settings import Settings
from .agents.tools import (
    generate_axis_unit_context,
    generate_ideal_roles,
    generate_actionable_context,
)

logger = logging.getLogger(__name__)


def _make_slug(text: str, max_len: int = 40) -> str:
    """Create a simple filesystem-safe slug from a string."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")
    return text or "run"


def _create_run_directory(settings: Settings) -> Path:
    """Create a per-run directory based on .env OUTPUT_BASE_DIR and timestamp."""
    base_dir = Path(settings.OUTPUT_BASE_DIR).expanduser().resolve()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    axis_slug = _make_slug(settings.AXIS_OF_EXPLORATION)
    unit_slug = _make_slug(settings.UNIT_OF_ANALYSIS)

    run_name = f"{timestamp}__axis-{axis_slug}__unit-{unit_slug}"
    run_dir = base_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Created run directory at %s", run_dir)
    return run_dir


def _write_step_output(run_dir: Path, filename: str, content: str) -> Path:
    """Write a single step's output to a file in the run directory."""
    path = run_dir / filename
    path.write_text(content, encoding="utf-8")
    logger.info("Wrote artefact: %s", path)
    return path


def execute_pipeline(settings: Settings, emit_console: bool = True) -> dict:
    """
    Core pipeline logic, reusable from CLI and FastAPI.

    Sequential steps:

      1. Generate the general context for AXIS × UNIT.
      2. From that context, generate the ideal roles prompt opening.
      3. From roles + context, generate an actionable analytical context brief.

    Returns a dict with:
      - run_dir (str)
      - step1_general_context
      - step2_ideal_roles_prompt
      - step3_actionable_context_brief
    """
    logger.info(
        "Executing pipeline: axis=%s | unit=%s | ideal_roles=%s",
        settings.AXIS_OF_EXPLORATION,
        settings.UNIT_OF_ANALYSIS,
        settings.IDEAL_ROLES,
    )

    # Create run directory
    run_dir = _create_run_directory(settings)

    if emit_console:
        print("\n🌐 BIG – Agentic Pipeline Run")
        print("====================================")
        print("We will now perform three internal steps:")
        print("  1️⃣ Generate a general analytical context for your AXIS × UNIT")
        print("  2️⃣ From that context, generate the ideal roles prompt opening")
        print(
            "  3️⃣ Using both, generate a rigorous, actionable analytical context brief\n"
        )

        print(f"   AXIS_OF_EXPLORATION: {settings.AXIS_OF_EXPLORATION}")
        print(f"   UNIT_OF_ANALYSIS   : {settings.UNIT_OF_ANALYSIS}")
        print(f"   COUNTRY            : {settings.COUNTRY}")
        print(f"   IDEAL_ROLES        : {settings.IDEAL_ROLES}")
        print(
            f"   EXTERNAL_RESEARCH  : "
            f"{'yes' if settings.EXTERNAL_RESEARCH else 'no'}"
        )
        print(f"   CONSTRAINTS        : {settings.CONSTRAINTS or 'none specified'}")
        print(f"   COMPLEX_UNIT       : {'yes' if settings.COMPLEX_UNIT else 'no'}\n")

        print(f"📁 This run will be saved to: {run_dir}\n")
        print("🚀 Launching sub-agents...\n")

    # ---------------------------
    # STEP 1: General context
    # ---------------------------
    logger.info("Step 1/3: generating general context via `generate_axis_unit_context`")

    context_block = generate_axis_unit_context.invoke(
        {
            "axis": settings.AXIS_OF_EXPLORATION,
            "unit": settings.UNIT_OF_ANALYSIS,
        }
    )
    _write_step_output(run_dir, "step1_general_context.md", context_block)

    if emit_console:
        print("✅ Step 1/3 completed.\n")
        print("====================================")
        print("STEP 1/3 – General context for AXIS × UNIT")
        print("====================================\n")
        print(context_block)
        print("\n------------------------------------\n")

    # ---------------------------
    # STEP 2: Ideal roles prompt
    # ---------------------------
    logger.info("Step 2/3: generating ideal roles via `generate_ideal_roles`")

    roles_block = generate_ideal_roles.invoke(
        {
            "context": context_block,
            "n_roles": settings.IDEAL_ROLES,
        }
    )
    _write_step_output(run_dir, "step2_ideal_roles_prompt.md", roles_block)

    if emit_console:
        print("✅ Step 2/3 completed.\n")
        print("====================================")
        print("STEP 2/3 – Ideal roles prompt opening")
        print("====================================\n")
        print(roles_block)
        print("\n------------------------------------\n")

    # ---------------------------
    # STEP 3: Actionable context brief
    # ---------------------------
    logger.info(
        "Step 3/3: generating actionable analytical context via "
        "`generate_actionable_context`"
    )

    actionable_block = generate_actionable_context.invoke(
        {
            "roles_prompt": roles_block,
            "general_context": context_block,
        }
    )
    _write_step_output(run_dir, "step3_actionable_context_brief.md", actionable_block)

    if emit_console:
        print("✅ Step 3/3 completed.\n")
        print("====================================")
        print("STEP 3/3 – Actionable analytical context brief (final output)")
        print("====================================\n")
        print(actionable_block)

        print(
            f"\n📝 All artefacts for this run are saved under:\n   {run_dir}\n"
            "   - step1_general_context.md\n"
            "   - step2_ideal_roles_prompt.md\n"
            "   - step3_actionable_context_brief.md\n"
        )

        print(
            "🎯 End of run – you can now reuse the final brief above as the "
            "context input for downstream ideation or opportunity generation."
        )

    logger.info("Run completed successfully. Artefacts stored at %s", run_dir)

    return {
        "run_dir": str(run_dir),
        "step1_general_context": context_block,
        "step2_ideal_roles_prompt": roles_block,
        "step3_actionable_context_brief": actionable_block,
    }


def run_once() -> None:
    """CLI entrypoint: load settings, configure logging, execute pipeline with console output."""
    settings: Settings = load_settings()
    setup_logging(settings)
    execute_pipeline(settings, emit_console=True)


if __name__ == "__main__":
    run_once()

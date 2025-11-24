from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ..config import load_settings


def _build_llm() -> ChatOpenAI:
    """Local helper to create a small, fast chat model for tools."""
    settings = load_settings()
    model_name = "gpt-4.1-mini"
    return ChatOpenAI(
        model=model_name,
        temperature=0.4,
        api_key=settings.OPENAI_API_KEY or None,
    )


@tool
def generate_axis_unit_context(axis: str, unit: str) -> str:
    """
    Generate a structured analytical general context for a given axis + unit.

    The axis and unit are fully generic and can describe any field of analysis.
    """
    llm = _build_llm()

    system = SystemMessage(
        content=(
            "You are a senior strategy consultant. You write clear, structured "
            "analytical briefs that can serve as a reusable context block for "
            "further AI prompts, regardless of the domain."
        )
    )

    user = HumanMessage(
        content=(
            "You are given an axis of exploration and a unit of analysis.\n\n"
            f"AXIS_OF_EXPLORATION: {axis}\n"
            f"UNIT_OF_ANALYSIS: {unit}\n\n"
            "Your task is to produce a self-contained, well-structured general "
            "context block, following this logic:\n\n"
            "-- START OF GENERAL CONTEXT --\n"
            "🔹 AXIS — <axis name in title case>\n\n"
            "Context of the axis\n"
            "Explain what this axis focuses on in terms of transformations, "
            "dynamics, behaviours, markets, technologies, or other relevant aspects "
            "in the field defined by the axis.\n\n"
            "Then, in bullet points, describe:\n"
            "- key transformations / dynamics related to this axis\n"
            "- typical opportunity zones (without listing specific business ideas)\n\n"
            "🎯 Objective of the axis:\n"
            "Summarise the strategic purpose of exploring this axis: what we are "
            "trying to understand, anticipate or identify.\n\n"
            "🧠 Analytical strategies:\n"
            "List 1–3 analytical strategies or angles that are particularly relevant "
            "for analysing this axis and the chosen unit of analysis.\n\n"
            "Finally, clearly state the UNIT OF ANALYSIS with a short parenthetical "
            "description of what is most important about it in this context.\n\n"
            "The tone should be analytical, neutral and reusable in other prompts.\n"
            "Return ONLY the formatted block including the boundary markers:\n"
            "`-- START OF GENERAL CONTEXT --` and `-- END OF GENERAL CONTEXT --`.\n"
        )
    )

    response = llm.invoke([system, user])
    return response.content


@tool
def generate_ideal_roles(context: str, n_roles: int) -> str:
    """
    From a general context text block, infer the ideal roles an AI should embody
    to analyse this field with high added value.

    This is fully generic and applies to any axis / unit combination.
    """
    llm = _build_llm()

    system = SystemMessage(
        content=(
            "You are an expert in designing analytical workflows and role-based AI "
            "collaboration. You decompose a field of analysis into complementary, "
            "well-defined analytical roles."
        )
    )

    user = HumanMessage(
        content=(
            "At the end of this prompt there is a block of text which describes a "
            "field of analysis, a strategic objective, a transformation area, or an "
            "issue to be explored.\n\n"
            "Relying solely on this content:\n\n"
            f"1. Infer {n_roles} ideal roles that an artificial intelligence should "
            "embody in order to provide rigorous, cross-cutting analysis with very "
            "high added value.\n\n"
            "Expected format: an opening to the prompt that can be directly used as "
            "the first part of a prompt: it must begin with "
            "‘You will embody the following roles to analyse <theme>:’ where you "
            "infer the theme from the context.\n\n"
            "Then simply list the roles, numbered, with **bold names** and one "
            "concise sentence describing what is expected from each role.\n\n"
            "Do NOT explain your reasoning. Do NOT add comments before or after. "
            "Return only the final prompt opening.\n\n"
            "--START OF TEXT BLOCK--\n"
            f"{context}\n"
            "--END OF TEXT BLOCK--"
        )
    )

    response = llm.invoke([system, user])
    return response.content


@tool
def generate_actionable_context(roles_prompt: str, general_context: str) -> str:
    """
    From the roles prompt opening (step 2) and the general context (step 1),
    produce a rigorous, cross-cutting and actionable analytical context brief.

    It must strictly follow the output structure and rigour principles defined
    in the internal instructions, and use only the provided context plus
    the configured variables (axis, unit, country, constraints, etc.).
    """
    settings = load_settings()
    llm = _build_llm()

    axis = settings.AXIS_OF_EXPLORATION
    unit = settings.UNIT_OF_ANALYSIS
    country = settings.COUNTRY
    external_research = settings.EXTERNAL_RESEARCH
    constraints = settings.CONSTRAINTS or "none specified"
    complex_unit = settings.COMPLEX_UNIT

    external_flag = "yes" if external_research else "no"
    complex_flag = "yes" if complex_unit else "no"

    # If the general_context already includes the boundary markers, reuse as is.
    if "-- START OF GENERAL CONTEXT --" in general_context:
        prompt_general = general_context
    else:
        prompt_general = (
            "-- START OF GENERAL CONTEXT --\n"
            f"{general_context}\n"
            "-- END OF GENERAL CONTEXT --"
        )

    system = SystemMessage(
        content=(
            "You are a neutral, rigorous strategy analyst. You produce structured, "
            "traceable analytical briefs that can be reused for later ideation "
            "without suggesting any concrete solutions."
        )
    )

    user_text = f"""
{roles_prompt}

You must produce a rigorous, cross-cutting and actionable analysis in order to identify
viable commercial opportunities from the 'General context' below, and solely from this content.

MISSION (Context only):  
Produce a rigorous, neutral and actionable context brief based on the 'General context' below,
and only on this content (unless [[EXTERNAL_RESEARCH]] = yes, see Rules).  
⚠️ FORBIDDEN at this stage: proposing solutions, offers, business models, channels, MVPs,
scorecards, GTM, or a shortlist of ideas.

Variables:  
• [[AXIS_OF_EXPLORATION]] = {axis}
• [[UNIT_OF_ANALYSIS]] = {unit}
• [[COUNTRY]] = {country}
• [[EXTERNAL_RESEARCH]] = {external_flag} (default: no)  
• [[CONSTRAINTS]] = {constraints}
• [[COMPLEX_UNITS]] = {complex_flag} (default: no) → adjust the length

Rigour principles (mandatory):  
• Neutrality: no value judgements and no ideological narrative.  
• Traceability: tag each relevant statement with [FAIT], [HYP] (minimal hypothesis),
  [INT] (interpretation/implication).  
• Parsimony: no external information beyond the General context; if [[EXTERNAL_RESEARCH]] = yes,
  cite the source after the statement: [SOURCE: domain, short title].  
• Explicit logic: make explicit ‘observation → mechanism → consequence → implication for (future) ideation’.  
• Qualitative quantification: if there is no data, use ordinal scales (low/medium/high) + short justification.  
• Replicability: stable, verifiable structure, ready to be reused by the ideation stage.

Target length:  
• By default: 300–500 words.  
• If [[COMPLEX_UNITS]] = yes: 700–900 words and +1 table ‘Trend | Risk | Opportunity | Critical unknown’.

Inclusion/exclusion rules:  
• Include: facts, country constraints, actors, value chain, needs/JTBD, frictions, unknowns, metrics to monitor.  
• Exclude: ideas, solution directions, evaluation, GTM, offer comparisons, MVP, pricing, business model.

OUTPUT FORMAT (use exactly this structure and these headings):

1. Neutral summary (≤ 8 lines)  
    – Object of the unit, country scope, why the topic is non-trivial for (future) ideation. [INT]
    
2. Scope & definitions  
    – Reformulation of the objective in 1–2 sentences. [INT]  
    – Key terms/segments and units explicitly mentioned. [FAIT]
    
3. Facts & observable signals  
    – List of elements explicitly present in the General context (trends, constraints, behaviours, internal figures if any). [FAIT]
    
4. Actors & value chain (table)  
    • Actor/Segment  
    • Role  
    • Purchasing power/influence (L/M/H)  
    • Incentives  
    • Country/specific constraints  
    (Tag each cell: [FAIT] if explicit, otherwise minimal [HYP])
    
5. Country environment & contextual constraints  
    – Regulation, culture, language, infrastructures, seasonality, dominant channels (if present). [FAIT]  
    – Critical unknowns if information is absent, formulated minimally. [HYP]
    
6. Needs-oriented segmentation (no solution)  
    – Relevant segments (2–6).  
    – For each segment: needs, constraints, ‘moments of truth’ / frictions. [INT] (+ [HYP] if needed)
    
7. Jobs-to-be-done (by segment)  
    – 3–7 JTBD per segment: ‘When [situation], I want [motivation] so that [outcome].’ [INT]  
    – Indicate the desired outcome (perceived success) and a plausible measurement proxy. [HYP] if missing.
    
8. Hypotheses & unknowns to clarify  
    – Prioritised list of questions that will condition ideation (feasibility, distribution, acceptance, legality). [HYP]  
    – For each: type of evidence required in the next phase (e.g. market data, interviews, purchase signals).
    
9. Indicators to monitor (leading metrics & proxies)  
    – 5–10 indicators (e.g. problem frequency, average basket size, decision delay, cost of channel access).  
    – For each indicator: Why it matters [INT] + How to observe it later [HYP].
    
10. Safeguards for the ideation stage (framing memory, no solutions)  
    – Briefly recall the relevant constraints from the context (e.g. limited capital, speed of execution,
      country/CV fit if provided). [INT]  
    – Do not formulate any proposal: only the constraints to be respected later.
    
11. Annex – Traceability log  
    – Complete list structured by tag: [FAIT] / [HYP] / [INT].  
    – If [[EXTERNAL_RESEARCH]] = yes: add the SOURCE for each external fact.
    

Style constraints:  
• Clear, concise, no storytelling and no superlatives.  
• Define any technical term in 1 sentence if used.  
• Never invent numerical data; if information is missing, formulate the minimal inference [HYP] and its impact.  
• No solution suggestions, no ideas, no evaluation at this stage.

PROMPT BLOCK 4 – General context to use strictly as the base:

{prompt_general}
"""

    user = HumanMessage(content=user_text)

    response = llm.invoke([system, user])
    return response.content

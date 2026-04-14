import json
import os
import re
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


DEFAULT_TEXT_COLS = [
    "habit_desc",
    "challenges",
    "triggers",
    "past_interventions",
    "motivation_stop",
    "interest_in_product",
    "liked_features",
    "app_improve",
    "other_comments",
]


def combine_text(row: pd.Series, cols: Iterable[str]) -> str:
    return " ".join(
        str(row[col]).strip()
        for col in cols
        if col in row.index and pd.notna(row[col]) and str(row[col]).strip()
    )


def clean_text(text: Optional[str]) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def prepare_feedback_dataframe(
    df: pd.DataFrame,
    text_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    text_cols = text_cols or DEFAULT_TEXT_COLS
    prepared = df.copy()
    prepared["all_text"] = prepared.apply(lambda row: combine_text(row, text_cols), axis=1)
    prepared["all_text_clean"] = prepared["all_text"].apply(clean_text)
    return prepared


def top_words(series: pd.Series, min_df: int = 1, n: int = 10) -> pd.DataFrame:
    cleaned = series.fillna("").map(clean_text)
    if cleaned.str.len().sum() == 0:
        return pd.DataFrame(columns=["word", "count"])

    vec = CountVectorizer(stop_words="english", min_df=min_df)
    matrix = vec.fit_transform(cleaned)
    counts = np.asarray(matrix.sum(axis=0)).ravel()
    words = np.array(vec.get_feature_names_out())
    return (
        pd.DataFrame({"word": words, "count": counts})
        .sort_values("count", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def make_frequency_table(text_series: pd.Series, min_df: int = 1, n: int = 15) -> pd.DataFrame:
    return top_words(text_series, min_df=min_df, n=n)


def get_user_examples(df: pd.DataFrame, limit: int = 6) -> List[str]:
    return df["all_text"].dropna().tolist()[:limit]


def build_simulation_prompt(
    persona_name: str,
    persona: Dict,
    scenario: Dict,
    examples: List[str],
    interaction_specs: Dict,
    product_brief: str,
) -> str:
    examples_block = "\n".join(f"- {example}" for example in examples[:4])
    return f"""
You are simulating a synthetic participant in an interaction-level UX evaluation of Habit Bandz.

Stay fully in character as the participant.
Focus on concrete physical interaction, timing, hesitation, attention, and workflow friction.
Return valid JSON only.
Do not include markdown fences.

PRODUCT BRIEF:
{product_brief}

PERSONA:
Name: {persona_name}
Description: {persona["description"]}
Needs: {", ".join(persona["needs"])}
Pain points: {", ".join(persona["pain_points"])}

INTERACTION SPECS:
{json.dumps(interaction_specs, indent=2)}

SCENARIO:
ID: {scenario["scenario_id"]}
Context: {json.dumps(scenario["context"], indent=2)}
Task: {scenario["task"]}

REAL USER LANGUAGE EXAMPLES:
{examples_block}

Return a JSON object with exactly these fields:
{{
  "persona_name": "{persona_name}",
  "scenario_id": "{scenario["scenario_id"]}",
  "would_use_wearable": true,
  "would_open_app": false,
  "interaction_walkthrough": ["step 1", "step 2", "step 3"],
  "micro_frictions": ["..."],
  "button_easy_to_locate": 1,
  "button_easy_to_press": 1,
  "certainty_press_registered": 1,
  "wearable_usefulness_in_context": 1,
  "app_usefulness_in_context": 1,
  "cognitive_load": 1,
  "discretion_in_public": 1,
  "fit_for_urge_moment": 1,
  "time_to_first_action_sec": 0.0,
  "time_to_successful_press_sec": 0.0,
  "missed_press_attempts": 0,
  "hesitation_moments": 0,
  "needed_visual_confirmation": true,
  "abandoned_interaction": false,
  "design_implication": "...",
  "quote_in_character": "..."
}}

Rules:
- Use 1 to 5 scales where 1 = very poor and 5 = excellent.
- Keep the walkthrough concrete and embodied.
- Do not invent product features not described.
- This is exploratory scenario testing, not a substitute for user research.
""".strip()


def create_genai_client(api_key: str):
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError(
            "google-genai is not installed. Install it before running the simulation notebook."
        ) from exc

    os.environ["GEMINI_API_KEY"] = api_key
    return genai.Client(api_key=api_key)


def run_simulation(
    client,
    persona_name: str,
    persona: Dict,
    scenario: Dict,
    interaction_specs: Dict,
    examples: List[str],
    product_brief: str,
    model_name: str = "gemini-2.5-flash",
) -> Dict:
    prompt = build_simulation_prompt(
        persona_name=persona_name,
        persona=persona,
        scenario=scenario,
        examples=examples,
        interaction_specs=interaction_specs,
        product_brief=product_brief,
    )

    text = None
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        text = (response.text or "").strip().replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        parsed.setdefault("persona_name", persona_name)
        parsed.setdefault("scenario_id", scenario["scenario_id"])
        return parsed
    except Exception as exc:
        return {
            "persona_name": persona_name,
            "scenario_id": scenario["scenario_id"],
            "error": str(exc),
            "raw_output": text,
        }


def flatten_simulation_results(results: List[Dict]) -> pd.DataFrame:
    if not results:
        return pd.DataFrame()
    return pd.json_normalize(results)


def add_simulation_metrics(results_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return results_df

    scored = results_df.copy()
    score_cols = [
        "button_easy_to_locate",
        "button_easy_to_press",
        "certainty_press_registered",
        "wearable_usefulness_in_context",
        "app_usefulness_in_context",
        "cognitive_load",
        "discretion_in_public",
        "fit_for_urge_moment",
        "time_to_first_action_sec",
        "time_to_successful_press_sec",
        "missed_press_attempts",
        "hesitation_moments",
    ]

    for col in score_cols:
        if col not in scored.columns:
            scored[col] = pd.NA
        scored[col] = pd.to_numeric(scored[col], errors="coerce")

    button_cols = [
        "button_easy_to_locate",
        "button_easy_to_press",
        "certainty_press_registered",
    ]
    workflow_cols = [
        "wearable_usefulness_in_context",
        "app_usefulness_in_context",
        "cognitive_load",
        "discretion_in_public",
        "fit_for_urge_moment",
    ]

    scored["mean_button_score"] = scored[button_cols].mean(axis=1)
    scored["mean_workflow_score"] = scored[workflow_cols].mean(axis=1)
    scored["high_button_friction"] = (
        (scored["button_easy_to_locate"] <= 2)
        | (scored["button_easy_to_press"] <= 2)
        | (scored["certainty_press_registered"] <= 2)
    )
    scored["high_workflow_friction"] = (
        (scored["fit_for_urge_moment"] <= 2)
        | (scored["cognitive_load"] <= 2)
    )
    scored["slow_interaction"] = scored["time_to_successful_press_sec"].fillna(0) > 3
    return scored


def summarize_by_scenario(results_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return pd.DataFrame()

    return (
        results_df.groupby("scenario_id", dropna=False)
        .agg(
            mean_button_score=("mean_button_score", "mean"),
            mean_workflow_score=("mean_workflow_score", "mean"),
            avg_time_to_press=("time_to_successful_press_sec", "mean"),
            avg_missed_presses=("missed_press_attempts", "mean"),
            pct_high_button_friction=("high_button_friction", "mean"),
            pct_high_workflow_friction=("high_workflow_friction", "mean"),
            pct_slow_interaction=("slow_interaction", "mean"),
        )
        .reset_index()
    )

# Habit Bandz

## Translating Qualitative Research into Product Direction Through Lightweight NLP, Behavioral Segmentation, and AI-Assisted UX Simulation

## Overview

This project documents a research-to-product workflow built for Habit Bandz, a behavioral health platform combining a wearable device, companion app, and clinician-facing dashboard.

The central problem was one of translation: how do you convert messy qualitative interview data into product decisions that are defensible, repeatable, and specific enough to act on?

The pipeline moves through four stages:

1. Input normalization and merging across two data sources
2. Lightweight NLP-based signal detection
3. Behavioral persona synthesis grounded in validated clinical subtypes
4. Structured AI simulation across persona-scenario combinations

The public repository version is a redacted, synthetic reconstruction of that workflow so the methodology can be shared without exposing private research materials.

## Problem Context

Habit Bandz presents a harder-than-average product design problem. The user is often cognitively overloaded at the exact moment the product needs to work. The target behavior can be automatic, stress-reactive, or only partially conscious. The experience spans physical and digital surfaces. And the product serves two stakeholders, patients and clinicians, with meaningfully different data and interaction needs.

Standard usability framing underspecifies this problem. What was needed was a behavior-aware systems model: one that could answer not just whether users liked the concept, but how different behavioral profiles would affect intervention success, workflow tolerance, and downstream data interpretation.

## Research Questions

1. What recurring signals appear in participant language around urges, compulsive behavior, and barriers to change?
2. Which signals are strong enough to inform product decisions?
3. How can those signals be formalized into user models that are behaviorally meaningful rather than descriptively convenient?
4. How can those models be used to pressure-test design assumptions before additional live evaluation?

## Repository Structure

The original project was organized as a staged analysis pipeline. This public repository contains a condensed, GitHub-friendly version of that work:

```text
Habit-Bandz-UX-Case-Study/
├── CASE_STUDY.md
├── README.md
├── requirements.txt
└── public_notebooks/
    ├── 01_habitbandz_user_insight_workflow.ipynb
    ├── 02_persona_simulation_exploration.ipynb
    ├── habitbandz_portfolio_utils.py
    ├── README.md
    └── data/
        └── habitbandz_synthetic_feedback.csv
```

## Pipeline

### Stage 1 - Input Normalization and Merging

Two CSV sources were loaded and merged in the original workflow: pre-trial marketing interview notes and post-trial product feedback. Both files shared the same schema but were collected at different points in the study. Each was transposed from wide to long format, then merged using `combine_first`, with post-trial data taking priority where records overlapped.

Column names were standardized from raw survey question text to shorter identifiers:

| Raw Field | Renamed |
| --- | --- |
| `Please describe your Habit.` | `habit_desc` |
| `Triggers? When do you do this?` | `triggers` |
| `Challenges?` | `challenges` |
| `What did you enjoy about using Habit Bandz...` | `liked_features` |
| `What features...would you change, add, or improve?` | `app_improve` |
| `On a scale of 1-5, how likely are you to recommend...` | `recommend_score` |

The merged dataset contained 21 rows and 53 columns. Several fields, including `past_interventions`, `motivation_stop`, and `other_comments`, were absent from the merged frame due to missingness in both sources and were excluded from downstream analysis.

### Stage 2 - Lightweight NLP for Signal Detection

Given the dataset size, small and qualitative, the NLP layer was intentionally simple and auditable.

Available text fields were concatenated into a single `all_text` field per participant, then cleaned via:

- lowercasing
- punctuation removal
- whitespace normalization

Two vectorization passes were run:

- Corpus-level frequency analysis using `CountVectorizer(stop_words="english", min_df=2)` on `all_text` to surface terms appearing across at least two participants
- Field-level frequency analysis using `CountVectorizer(stop_words="english", min_df=1)` run separately on individual columns to identify field-specific signal

Top corpus-level terms included `pick`, `habit`, `stop`, `hair`, `skin`, `nails`, `app`, and `easy`, consistent with the BFRB and compulsive habit profile of the participant pool.

Exploratory clustering was run using `KMeans(n_clusters=3, random_state=42, n_init=10)` on the raw count matrix from the corpus vectorizer. Cluster assignments were treated as hypothesis generators to be validated against the clinical literature, not as final segments.

Manual review ran in parallel. Close reading of raw responses identified patterns the frequency outputs could not surface, particularly around awareness level at the moment of behavior and the distinction between stress-reactive and absentminded urge onset.

Four core themes were coded:

| Theme | Example Signals |
| --- | --- |
| Awareness Issues | automatic behavior, not noticing, zoning out |
| Stress-Driven Behavior | stress, anxiety, overwhelm |
| Need for Low-Friction Interaction | faster logging, fewer steps, clear navigation |
| Value of Physical Intervention | bracelet reminder, physical cue, interrupt behavior |

### Stage 3 - Behavioral Persona Synthesis

The persona framework is grounded in den Ouden et al. (2022), "Parsing compulsivity and cognitive control in alcohol use disorder and obsessive compulsive disorder," published in *Translational Psychiatry*.

That paper identified three clinically validated compulsive behavioral subtypes using a transdiagnostic sample, characterized along dimensions of compulsivity severity, behavioral avoidance, stress reactivity, and learning bias:

| Subtype | Compulsivity | Stress / Avoidance | Learning Bias | CAR |
| --- | --- | --- | --- | --- |
| Compulsive Non-Avoidant (CNA) | Mild-moderate | Low stress, low avoidance | Negative | Low |
| Compulsive Reactive (CR) | Mild-moderate | Mild stress, mild avoidance | Strong positive | High |
| Compulsive Stressed (CS) | Moderate-severe | High stress, high avoidance | Positive | Moderate |

These subtypes mapped directly onto the qualitative clustering outputs and were adopted as the persona framework. The demographic and behavioral profiles below were synthesized from the study data for product application purposes:

| Profile | Age | SES | Stress | Behavioral Style |
| --- | --- | --- | --- | --- |
| CNA | Older | Higher | Low | Stable, low-reactivity |
| CR | Younger | Mixed | Moderate | Reward-driven, adaptive |
| CS | Working-age | Lower | High | Overloaded, avoidant |

Each persona was defined with a short description, core needs, and primary pain points structured to map directly onto product failure modes rather than user identity traits.

Using clinically validated subtypes rather than purely inductive archetypes strengthens downstream product reasoning and opens a credible path toward subtype-aware personalization as the platform matures.

### Stage 4 - AI-Assisted Scenario Simulation

Structured prompts were used to simulate how each persona would interact with the product across five scenarios chosen to represent the highest-friction conditions identified in testing:

| Scenario | Context |
| --- | --- |
| `bathroom_mirror_trigger` | Visually fixated, habit escalating gradually |
| `late_night_scroll` | High fatigue, absentminded urge onset, one hand occupied |
| `walking_stress_urge` | Moving, sudden urge, split attention |
| `meeting_or_waiting_room` | Public setting, high social awareness, discreet use required |
| `review_progress_after_several_days` | Calm, reflective, evaluating whether the product is working |

Each prompt included:

- product brief
- persona attributes
- interaction specs for the wearable button and app logging flow
- scenario context
- grounding examples drawn from real participant language

Simulations were run using Gemini 2.5 Flash via the Google GenAI client, with structured output extracted using a Pydantic schema (`SimulationResult`). The full run produced 15 simulation records: 3 personas by 5 scenarios.

Scored dimensions included:

- button locatability
- ease of press
- press confirmation certainty
- wearable usefulness in context
- app usefulness in context
- cognitive load
- discretion in public
- fit for urge moment

Timing estimates and interaction counts were also requested per simulation, including time to first action, time to successful press, missed presses, and hesitation moments.

Output was used to identify likely friction before additional live evaluation, surface scenario-specific risk differences across subtypes, and generate a prioritized list of hypotheses for the next research phase.

## Key Findings

Several behavioral signals recurred consistently across the dataset:

- Automatic or semi-automatic behavior frequently delayed intervention; participants were often mid-behavior before awareness registered.
- Stress and cognitive overload amplified the need for immediate, low-friction response; multi-step interactions failed at the highest-value moments.
- Physical interruption was valued when fast and reliable; perceived latency eroded trust in the system.
- CNA participants showed a distinct need for interpretable trend data, not just event logging, implying meaningfully different feature needs across subtypes.

## Product Implications

### Intervention Design

The data pointed toward a physical interaction model prioritizing:

- tactile feedback
- minimal visual dependence
- low motor burden
- low cognitive burden

For CR and CS users especially, every additional interaction step is a failure risk.

### Logging Architecture

Logging should optimize for speed first, completeness second. A flow requiring reflective input during a stress-reactive moment will fail for the users who most need it.

A minimal capture-now, enrich-later model is more consistent with observed behavior across all three subtypes.

### Progress Visibility

CNA users showed a distinct need for:

- trend clarity
- timestamp granularity
- explicit interpretation support

This implies either a bifurcated data presentation model or adaptive views keyed to detected subtype.

### Personalization

The clinical subtype framework suggests a credible path toward behavioral-profile-driven personalization: adapting intervention flow, logging burden, follow-up prompts, and default views based on user profile.

A longer-term direction worth exploring is using subtype classification as a basis for predictive modeling, anticipating high-risk moments by profile rather than responding to them after the fact. That work would require longitudinal behavioral data the platform does not yet have, but the subtype framework is already structured to support it.

## Data

The original project relied on private interview-note datasets. The public repository includes synthetic data that mirrors the schema and general distributional properties of the original qualitative dataset without including any real participant data.

That synthetic dataset is suitable for reproducing the public workflow and experimenting with the NLP and simulation components.

## Methods and Tools

| Component | Detail |
| --- | --- |
| Data merging | `pandas.DataFrame.combine_first`, wide-to-long transpose |
| Text preprocessing | lowercasing, regex punctuation removal, whitespace normalization |
| Corpus frequency analysis | `CountVectorizer(stop_words="english", min_df=2)` |
| Field-level frequency analysis | `CountVectorizer(stop_words="english", min_df=1)` |
| Clustering | `KMeans(n_clusters=3, random_state=42, n_init=10)` on raw count matrix |
| Persona synthesis | Clustering outputs validated against den Ouden et al. (2022) |
| Simulation model | Gemini 2.5 Flash via Google GenAI client |
| Structured output | Pydantic `SimulationResult` schema |

## Limitations

- The dataset is small and qualitative; clustering results should be interpreted as exploratory rather than statistically robust.
- Several expected text fields, including `past_interventions`, `motivation_stop`, and `other_comments`, were absent from the merged dataframe due to missingness across both sources, limiting the breadth of the frequency analysis.
- Persona boundaries are fuzzy in practice; real users exhibit mixed profiles, particularly under varying stress conditions.
- The demographic profiles synthesized for product use are approximations; direct replication of the clinical sample characteristics was not the goal.
- Simulation outputs reflect both prompt design choices and the limitations of synthetic participant methodology.

## Reference

den Ouden, H. E. M., et al. (2022). *Parsing compulsivity and cognitive control in alcohol use disorder and obsessive compulsive disorder*. Translational Psychiatry, 12, 425. https://doi.org/10.1038/s41398-022-02186-2

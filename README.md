# Occupational Representations Survey

## Overview

We developed novel computationally-grounded tasks to assess the dimensions individuals use to navigate occupational space, with four key design innovations.

**Personalized stimuli.** Tasks were fully personalized to each participant's primary occupation: participants indicated their current or most recent role, which was matched to the O\*NET database using OpenAI text embeddings, and participants selected the best match from the five most semantically similar occupation titles. This anchor occupation defined the stimulus space for all subsequent tasks, making the design sensitive to each participant's actual position in occupational space rather than a generic set of occupations. All inter-occupation distances were computed as cosine distances over O\*NET ratings vectors, separately for each SKA dimension.

**Forced-choice stimuli designed to discriminate dimensions.** We identified a neighborhood of candidate occupations for each dimension by applying a distance threshold calibrated to ensure a sufficient candidate pool, then selected pairs exhibiting a distance inversion across dimensions: one occupation was closer to the anchor on the focal dimension while the other was closer on the contrasting dimension. Each trial therefore placed the two dimensions in direct competition, isolating dimensional preference from general similarity. Two tasks were constructed in this way: Task 1 contrasted Skill neighbors with Work Activity neighbors, and Task 2 contrasted Skill neighbors with Knowledge neighbors, each comprising 30 trials.

**Ranking stimuli representing all three dimensions simultaneously.** We identified the 15 closest occupations to the anchor for each SKA dimension based on cosine distance, removed duplicates across the three lists, and retained the top 5 occupations per dimension, yielding 15 occupations in total (3 × 5). Participants ranked all 15 by similarity to their anchor, providing a complementary implicit measure of dimensional prioritization.

---

## App Structure

The survey is built in [oTree](https://www.otree.org/) and consists of the following apps, listed in order of participant flow:

### `representations_v2` — Consent & Anchor Occupation
Entry point for the study. Collects informed consent and identifies each participant's current or most recent occupation. The entered job title is matched to O\*NET via OpenAI text embeddings (`text-embedding-ada-002`); participants select the best match from five candidates, with up to 5 retry attempts. The selected O\*NET occupation becomes the anchor job used throughout all subsequent tasks.

### `occupationinfo` — Job Details
Collects open-ended information about the participant's current role: years in the position, primary skills used, and main job duties. All fields are optional.

### `representations_task_s_wa` — Forced-Choice Task 1: Skills vs. Work Activities
Presents 30 forced-choice trials. On each trial, participants see two occupations and choose which is more similar to their anchor. Pairs are constructed so that one occupation is a closer Skills neighbor and the other is a closer Work Activities neighbor, placing the two dimensions in direct competition. Response choices and times are recorded; choice patterns are summarized as counts of Skills-aligned vs. Work-Activities-aligned responses.

### `representations_task_s_k` — Forced-Choice Task 2: Skills vs. Knowledge
Identical design to Task 1 but contrasting Skills neighbors against Knowledge neighbors across 30 trials. Produces counts of Skills-aligned vs. Knowledge-aligned choices.

### `occupation_ranking` — Occupational Similarity Ranking
Participants rank 15 occupations by overall similarity to their anchor job. The 15 occupations are drawn from the top-5 closest neighbors on each of the three SKA dimensions (Skills, Knowledge, Work Activities), with duplicates removed. Ranking order is recorded as an implicit measure of dimensional prioritization.

### `similarity_transition_ranking` — Explicit Dimension Rankings
Two drag-to-rank pages capturing stated preferences. The first asks participants to rank 7 factors by importance for perceiving job similarity (Skills, Tasks, Knowledge, Work Environment, Education and Training, Personal Values, Industry/Sector). The second asks them to rank 9 factors by importance for job transition feasibility (Annual Income, Work-Life Balance, Company Culture, Career Growth Opportunities, Geographic Location, Educational Requirements, Skill Overlap, Task Overlap, Social Status). Factor lists are shuffled per participant.

### `values_ranking` — Work Values Ranking
Participants rank 6 O\*NET work values (Achievement, Independence, Recognition, Relationships, Support, Working Conditions) by personal importance, with brief descriptions shown for each. Rankings are used downstream to compute values alignment with the participant's current, attainable, and dream occupations.

### `attainable_occupation` — Attainable Job
Participants enter a job they would be both interested in and qualified for given their current skills and experience. The title is matched to O\*NET via the same embedding pipeline as the anchor occupation, with up to 3 retry attempts.

### `dream_occupation` — Dream Job
Participants enter a dream job with no constraints (no need to retrain, relocate, or worry about money). Matched to O\*NET via the same embedding pipeline, with up to 3 retry attempts.

### `transition_q` — Career Transition Context
Two pages collecting career intentions: whether the participant is considering changing careers or jobs, their approximate timeframe, and open-ended responses about their top hopes and concerns regarding a career transition.

### `representations_q_1` — Demographics & PDF Report
Collects demographic information (education, age, gender, income, ethnicity) and generates a personalized PDF report for each participant. The report includes:
- Participant summary (demographics, anchor/attainable/dream jobs)
- An explanation of the O\*NET framework and study methodology
- Occupational representations charts comparing reported (explicit ranking) vs. measured (task-derived) dimensional priorities across Skills, Knowledge, and Work Activities
- Values alignment showing how the participant's ranked values map onto their three occupations
- Gap-overlap analyses for skill transitions between current, attainable, and dream jobs

Reports are saved to `_static/reports/{session_code}_{participant_code}_{id}/` and participants receive a download link.

### `go_no_go` — Go/No-Go Cognitive Task
A brief reaction-time task presenting 10 images sequentially. Participants respond to designated "go" stimuli and withhold responses to "no-go" stimuli. Errors and response patterns are recorded per trial.

---

For setup and running instructions, see [SETUP.md](SETUP.md).

---

## Note on Excluded Files

The following files are tracked via Git LFS and are **not included** in this repository due to storage limitations:

- `_static/all_embed2.csv`
- `attainable_occupation/job_match.csv`
- `dream_occupation/job_match.csv`
- `occupation_ranking/target_jobs_skwa.csv`
- `representations_q_1/k_vec.csv`, `knowledge.csv`, `s_vec.csv`, `skills.csv`, `value_vec.csv`, `values.csv`, `wa_vec.csv`
- `representations_task_s_k/master_dist_skwa.csv`, `triplets_30_k_s.csv`
- `representations_task_s_wa/master_dist_skwa.csv`, `triplets_30_s_wa.csv`
- `representations_v2/job_match.csv`

These files contain precomputed O\*NET distance matrices and embeddings required to run the survey tasks. Contact the repository owner to obtain them.

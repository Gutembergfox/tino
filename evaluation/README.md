# Linguistic evaluation protocol — not yet run

This is a small **AI-assisted, provisional test set**, not an expert-labelled benchmark. The 12 original synthetic cases include English and Brazilian Portuguese, three registers, six explicit no-change cases, register shifts, and ambiguous forms that should not automatically be diagnosed as Portuguese transfer. No client or learner data are included.

**Status:** case-structure validation and mocked software tests are separate from linguistic evaluation. No model calls, human ratings, accuracy, learning gains or production-quality claims are reported here. Independent linguistic review of the expected behaviours is pending.

## Before any live evaluation

1. Have a qualified PT/EN reviewer inspect the source text, intended audience and rationale for every case. Record revisions and disagreements. Freeze the reviewed case version before testing.
2. Specify the task context. Register judgments depend on audience, genre and purpose; a single label cannot settle every borderline choice.
3. Obtain authorization for any provider cost. Record the model/version, prompt commit, date, generation parameters and repetition count. Use only synthetic or consented material.
4. Save complete outputs and errors under a run ID. Do not cherry-pick successful runs. Report refusals, parsing failures and missing outputs.

## Rating rubric

Review each output against the source and declared context:

- **Contract:** valid schema, correct register, exact source quotes, and preservation of quotes/suggestions during UI translation.
- **No-change behaviour:** proportion of reviewed no-change cases returning zero annotations, reported with numerator/denominator (six provisional cases, not a population estimate).
- **Annotation precision:** relevant and justified annotations divided by all proposed annotations, with manual adjudication and explicit handling of zero annotations.
- **Coverage:** reviewed target issues addressed divided by the adjudicated issue inventory; do not invent a recall denominator before annotation.
- **Meaning preservation:** whether suggestions preserve intended meaning, certainty and factual claims.
- **Sociolinguistic calibration:** no stigmatization of variants; transfer explanations are hypotheses, not diagnoses inferred from nationality or isolated forms.
- **Language and usefulness:** explanations use the intended interface language and provide actionable, proportionate feedback.

Use two independent reviewers when feasible. Report agreement and adjudication separately. If only one reviewer is available, disclose it. Keep model identity hidden during rating where practical. Repeat generations to examine variability; report all repetitions and prompt changes rather than presenting a single favourable output.

## Offline check

```bash
python evaluation/validate_cases.py
```

This checks counts, IDs, register/language coverage and endpoint word limits only. It produces **no linguistic performance metric**. Mocked API responses are hand-built fixtures and must never be counted as model predictions.

The small synthetic set is suitable for development and regression planning. It cannot establish performance on real learners, dialect coverage, educational outcomes or safety across high-stakes uses.

Tenets for Building LLM Systems

Modern language models are powerful enough to make poorly designed systems appear to work. That is useful, but dangerous. A strong LLM system should not depend on a frontier model brute-forcing ambiguity, oversized context, vague interfaces, or messy data.

The goal is to use model intelligence deliberately.

1. Treat LLM calls as auditable software interfaces

When the task is known and repeatable, an LLM call should behave like a typed function.

The system should define:

* exactly what input the model receives
* exactly what output format is expected
* how the output is validated
* which prompt, model, and parameters were used
* how the result can be reproduced later

This is the gold standard for classification, extraction, scoring, summarization, and other repeatable inference tasks.

Example: if a model classifies Reddit posts for relevance, the output should not be free-form prose. It should be a structured result such as:

{
  "is_relevant": true,
  "reason": "Discusses a topic tracked by the knowledge base",
  "confidence": "medium"
}

The run should be tied to the exact input row, prompt version, model version, token count, and raw response.

2. Constrain known work; reserve agency for uncertainty

Do not give a model agency unless the task actually requires agency.

If the data structure is known, the workflow should usually be constrained. A model does not need to “explore” a CSV if the relevant columns are already known. It does not need to inspect an entire spreadsheet if deterministic code can select the necessary rows first.

Agents are appropriate when the target or path is uncertain.

Use constrained pipelines when:

* the input structure is known
* the task is repeatable
* the output shape is defined
* the success criteria can be tested

Use agents when:

* the relevant information may or may not exist
* the source structure is unknown
* the path to the answer is uncertain
* retrieval, judgment, and exploration are part of the task

Example: “Classify these 10,000 known posts” should be a pipeline.
“Check whether YouTube has relevant new material today and bring back anything useful” may justify an agent.

3. Design for model portability

A codebase should not depend on one provider or one frontier model.

Even when production uses a hosted frontier model, the architecture should make it possible to swap models. When feasible, it should support local models as a baseline. The local model does not have to be the best model; it functions as a design constraint.

Supporting smaller or local models forces the system to handle:

* explicit model interfaces
* token counting
* context-window checks
* chunking
* map-reduce or refine-style summarization
* benchmark comparisons
* graceful degradation

If a system works with a smaller model, stronger models become upgrades rather than dependencies.

Example: a YouTube transcript pipeline should know whether a transcript fits in context before calling the model. If it does not fit, the system should chunk and summarize deliberately rather than relying on a frontier agent to improvise its way through the file.

4. Show the model only the smallest sufficient data

An LLM or agent should see exactly the data it needs to do its job, and no more.

Before inference, the system should clean, filter, scope, and reshape the data. Metadata should be withheld unless the model needs it for the task. IDs, timestamps, URLs, and auxiliary fields can often be reattached outside the model call.

This reduces:

* token cost
* distraction
* accidental signal
* privacy exposure
* failure ambiguity
* unnecessary dependence on model strength

Example: if the model is classifying whether a post is relevant based only on text, it may need the title and body. It may not need the post ID, timestamp, author, subreddit, URL, or scrape metadata. Those fields can remain in the surrounding data pipeline and be joined back after classification.

A preferred pattern is to save artifacts at each stage:

* cleaned pre-LLM input
* raw model output
* parsed/validated output
* final enriched dataset with metadata reattached

This makes the pipeline inspectable before and after inference.

5. Do deterministic narrowing before probabilistic reasoning

Software should prepare the task before the model reasons about it.

Do not hand a model an entire file, spreadsheet, transcript collection, or database table when code can first select the relevant subset. Even powerful agents perform better when the task has been narrowed.

Example: instead of asking an agent to search an entire CSV for relevant records, use deterministic code to select candidate rows, normalize fields, remove irrelevant columns, and then ask the model to judge only the remaining records.

The model should perform reasoning, not compensate for avoidable lack of preprocessing.

Core principle

Do not substitute model strength for system design.

Frontier models can tolerate messy inputs, weak interfaces, and excessive context. Durable systems should not rely on that. A good LLM system uses intelligence where intelligence is needed, while keeping everything else explicit, auditable, portable, and constrained.
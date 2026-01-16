uv run python -m examples.simulate \
    client=test \
    therapist=bad \
    event=therapySession \
    event.output_dir=data/sessions/default/badtherapist_test.json \
    event.max_turns=10 \
    event.langfuse=False \
    event.recursion_limit=1000 \
    lang=en \
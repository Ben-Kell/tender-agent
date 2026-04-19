PIPELINE_STAGES = [
    ("running_create_tender", "create_tender"),
    ("running_detect_returnable_documents", "detect_returnable_documents"),
    ("running_analyze_returnable_documents", "analyze_returnable_documents"),
    ("running_start_run", "start_run"),
    ("running_tm_pricing_csv", "generate_tm_pricing_csv"),
    ("running_map_template", "map_template"),
    ("running_draft_sections", "draft_sections"),
    ("running_compile_response", "compile_response"),
    ("evaluating_compliance", "evaluate_compliance"),
]
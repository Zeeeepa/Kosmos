# Test Coverage Gap Analysis

**Repository:** Kosmos AI Scientist
**Analysis Date:** 2025-11-29
**Testing Framework:** pytest with pytest-asyncio, pytest-cov, pytest-mock

---

## Summary

| Metric | Count |
|--------|-------|
| Total source files analyzed | 158 |
| Files with no test coverage | 70 |
| Files with partial coverage | 28 |
| Files with comprehensive coverage | 60 |
| **Critical priority gaps** | **15** |
| **High priority gaps** | **25** |
| **Medium priority gaps** | **20** |
| **Low priority gaps** | **10** |

### Coverage by Module

| Module | Source Files | Test Files | Coverage | Status |
|--------|--------------|------------|----------|--------|
| core/ | 23 | 7 | 30% | POOR |
| agents/ | 9 | 5 | 56% | PARTIAL |
| execution/ | 13 | 10 | 77% | GOOD |
| literature/ | 10 | 5 | 50% | PARTIAL |
| knowledge/ | 8 | 5 | 63% | PARTIAL |
| world_model/ | 5 | 4 | 80% | GOOD |
| orchestration/ | 4 | 4 | 100% | EXCELLENT |
| validation/ | 1 | 1 | 100% | EXCELLENT |
| hypothesis/ | 4 | 4 | 100% | EXCELLENT |
| safety/ | 4 | 4 | 100% | EXCELLENT |
| workflow/ | 1 | 1 | 100% | EXCELLENT |
| domains/ | 11 | 11 | 100% | EXCELLENT |
| compression/ | 1 | 1 | 100% | EXCELLENT |
| analysis/ | 4 | 1 | 25% | POOR |
| cli/ | 13 | 2 | 15% | POOR |
| api/ | 1 | 0 | 0% | CRITICAL |
| monitoring/ | 2 | 0 | 0% | CRITICAL |
| models/ | 5 | 0 | 0% | CRITICAL |
| db/ | 2 | 1 | 50% | PARTIAL |
| experiments/ | 18 | 1 | 6% | CRITICAL |
| utils/ | 2 | 0 | 0% | CRITICAL |
| oversight/ | 2 | 1 | 50% | PARTIAL |

---

## Critical Priority

These are core infrastructure components with zero test coverage that handle sensitive operations.

---

### kosmos/agents/base.py

**Location:** `kosmos/agents/base.py`
**Current Coverage:** None
**Lines of Code:** ~400
**Impact:** All agent subclasses inherit from BaseAgent - this is foundational

#### `BaseAgent` class (26+ public methods)

- **Gap:** Complete lack of tests for agent lifecycle, messaging, and state management
- **Recommended Tests:**

1. `test_base_agent_initialization` - Verify agent creates with correct ID, status, config
2. `test_base_agent_start_sets_running_status` - Verify start() transitions status to RUNNING
3. `test_base_agent_stop_sets_stopped_status` - Verify stop() transitions status to STOPPED
4. `test_base_agent_pause_resume_cycle` - Verify pause/resume lifecycle
5. `test_base_agent_send_message_creates_message` - Verify message creation with correlation ID
6. `test_base_agent_receive_message_queues_message` - Verify message queueing
7. `test_base_agent_process_message_calls_handler` - Verify handler dispatch
8. `test_base_agent_register_message_handler` - Verify handler registration
9. `test_base_agent_get_state_returns_current_state` - Verify state retrieval
10. `test_base_agent_restore_state_applies_state` - Verify state restoration
11. `test_base_agent_save_state_data_persists` - Verify state persistence
12. `test_base_agent_is_healthy_returns_true_when_running` - Verify health check
13. `test_base_agent_execute_abstract_raises` - Verify abstract method behavior
14. `test_base_agent_message_router_integration` - Verify router callback works
15. `test_base_agent_statistics_tracking` - Verify stats accumulation

**Mocking Requirements:** Mock LLM client, mock message router

---

### kosmos/agents/registry.py

**Location:** `kosmos/agents/registry.py`
**Current Coverage:** None
**Lines of Code:** ~350
**Impact:** Critical for multi-agent coordination

#### `AgentRegistry` class (24+ public methods)

- **Gap:** No tests for agent registration, message routing, or system health
- **Recommended Tests:**

1. `test_registry_register_agent_adds_to_registry` - Verify registration
2. `test_registry_register_duplicate_raises_error` - Verify duplicate handling
3. `test_registry_unregister_removes_agent` - Verify unregistration
4. `test_registry_get_agent_returns_registered` - Verify retrieval
5. `test_registry_get_agent_not_found_raises` - Verify error handling
6. `test_registry_get_agents_by_type_filters` - Verify type filtering
7. `test_registry_list_agents_returns_all` - Verify listing
8. `test_registry_start_agent_calls_start` - Verify lifecycle management
9. `test_registry_stop_agent_calls_stop` - Verify stop propagation
10. `test_registry_start_all_starts_all_agents` - Verify batch start
11. `test_registry_stop_all_stops_all_agents` - Verify batch stop
12. `test_registry_send_message_routes_correctly` - Verify message routing
13. `test_registry_broadcast_message_sends_to_all` - Verify broadcast
14. `test_registry_message_history_limited_by_size` - Verify history limits
15. `test_registry_get_system_health_aggregates` - Verify health aggregation
16. `test_registry_singleton_returns_same_instance` - Verify singleton pattern

**Mocking Requirements:** Mock BaseAgent instances

---

### kosmos/agents/experiment_designer.py

**Location:** `kosmos/agents/experiment_designer.py`
**Current Coverage:** None
**Lines of Code:** ~600
**Impact:** Core experiment design workflow

#### `ExperimentDesignerAgent` class

- **Gap:** No tests for experiment protocol design or validation
- **Recommended Tests:**

1. `test_designer_design_experiment_from_template` - Verify template-based design
2. `test_designer_design_experiment_with_llm` - Verify LLM-based design
3. `test_designer_select_experiment_type_matches_domain` - Verify type selection
4. `test_designer_validate_protocol_checks_required_fields` - Verify validation
5. `test_designer_validate_protocol_rejects_invalid` - Verify rejection
6. `test_designer_calculate_rigor_score_methodology` - Verify scoring
7. `test_designer_calculate_completeness_score` - Verify completeness
8. `test_designer_assess_feasibility_cost_limits` - Verify cost feasibility
9. `test_designer_assess_feasibility_duration_limits` - Verify duration feasibility
10. `test_designer_generate_recommendations` - Verify recommendation generation
11. `test_designer_design_experiments_batch` - Verify batch design
12. `test_designer_list_templates_returns_available` - Verify template listing
13. `test_designer_execute_message_handling` - Verify message-based execution
14. `test_designer_store_protocol_persists` - Verify database storage

**Mocking Requirements:** Mock ClaudeClient, mock database session

---

### kosmos/execution/jupyter_client.py

**Location:** `kosmos/execution/jupyter_client.py`
**Current Coverage:** None
**Lines of Code:** ~500
**Impact:** Security-critical async code execution in Docker

#### `JupyterClient` class

- **Gap:** No tests for async code execution - security critical
- **Recommended Tests:**

1. `test_jupyter_execute_code_success` - Verify successful execution
2. `test_jupyter_execute_code_with_timeout` - Verify timeout handling
3. `test_jupyter_execute_code_syntax_error` - Verify syntax error handling
4. `test_jupyter_execute_code_runtime_error` - Verify runtime error handling
5. `test_jupyter_execute_code_captures_stdout` - Verify stdout capture
6. `test_jupyter_execute_code_captures_stderr` - Verify stderr capture
7. `test_jupyter_execute_code_returns_result_variable` - Verify result extraction
8. `test_jupyter_execute_notebook_runs_cells` - Verify notebook execution
9. `test_jupyter_run_script_executes_file` - Verify script execution
10. `test_jupyter_check_package_returns_installed` - Verify package checking
11. `test_jupyter_install_package_installs` - Verify package installation
12. `test_jupyter_wrap_code_adds_capture` - Verify code wrapping
13. `test_jupyter_extract_error_parses_traceback` - Verify error extraction
14. `test_jupyter_parse_outputs_handles_types` - Verify output parsing
15. `test_jupyter_base64_code_transfer` - Verify encoding/decoding

**Mocking Requirements:** Mock Docker container, mock asyncio subprocess

---

### kosmos/execution/parallel.py

**Location:** `kosmos/execution/parallel.py`
**Current Coverage:** None
**Lines of Code:** ~400
**Impact:** Critical for batch experiment execution

#### `ParallelExperimentExecutor` class

- **Gap:** No tests for parallel execution - ProcessPoolExecutor critical path
- **Recommended Tests:**

1. `test_parallel_execute_batch_runs_all_tasks` - Verify all tasks execute
2. `test_parallel_execute_batch_respects_max_workers` - Verify worker limits
3. `test_parallel_execute_batch_handles_failure` - Verify failure handling
4. `test_parallel_execute_batch_aggregates_results` - Verify result aggregation
5. `test_parallel_execute_batch_tracks_progress` - Verify progress tracking
6. `test_parallel_execute_batch_async` - Verify async wrapper
7. `test_parallel_execute_single_experiment_serializes` - Verify serialization
8. `test_parallel_callbacks_on_complete` - Verify callback invocation
9. `test_parallel_task_prioritization` - Verify priority handling
10. `test_parallel_resource_scheduler_optimal_workers` - Verify adaptive scaling
11. `test_parallel_resource_scheduler_memory_pressure` - Verify memory awareness
12. `test_parallel_timeout_per_task` - Verify per-task timeout

**Mocking Requirements:** Mock ProcessPoolExecutor, mock execute_protocol_code

---

### kosmos/core/metrics.py

**Location:** `kosmos/core/metrics.py`
**Current Coverage:** None
**Lines of Code:** ~500
**Impact:** Budget tracking and cost monitoring - financial

#### `MetricsCollector` class

- **Gap:** No tests for API tracking or budget enforcement
- **Recommended Tests:**

1. `test_metrics_record_api_call_tracks_tokens` - Verify token tracking
2. `test_metrics_record_api_call_tracks_cost` - Verify cost calculation
3. `test_metrics_get_api_statistics_aggregates` - Verify statistics
4. `test_metrics_record_experiment_start_end` - Verify experiment tracking
5. `test_metrics_configure_budget_sets_limits` - Verify budget config
6. `test_metrics_check_budget_under_limit` - Verify budget check pass
7. `test_metrics_check_budget_over_limit_alerts` - Verify budget alerts
8. `test_metrics_budget_alert_thresholds` - Verify alert thresholds
9. `test_metrics_cache_hit_miss_tracking` - Verify cache metrics
10. `test_metrics_agent_statistics` - Verify agent metrics
11. `test_metrics_export_returns_all_data` - Verify export
12. `test_metrics_reset_clears_all` - Verify reset
13. `test_metrics_singleton_pattern` - Verify singleton

**Mocking Requirements:** None (pure data collection)

---

### kosmos/core/cache_manager.py

**Location:** `kosmos/core/cache_manager.py`
**Current Coverage:** None
**Lines of Code:** ~400
**Impact:** Core cache orchestration

#### `CacheManager` class

- **Gap:** No tests for cache type management or optimization
- **Recommended Tests:**

1. `test_cache_manager_get_cache_by_type` - Verify cache retrieval
2. `test_cache_manager_get_set_delete_operations` - Verify CRUD
3. `test_cache_manager_cleanup_expired_removes_old` - Verify cleanup
4. `test_cache_manager_get_stats_per_type` - Verify per-type stats
5. `test_cache_manager_warm_up_populates` - Verify warm-up
6. `test_cache_manager_get_size_breakdown` - Verify size tracking
7. `test_cache_manager_get_hit_rates` - Verify hit rate calculation
8. `test_cache_manager_optimize_evicts_least_used` - Verify optimization
9. `test_cache_manager_health_check_returns_status` - Verify health
10. `test_cache_manager_singleton_pattern` - Verify singleton

**Mocking Requirements:** Mock individual cache implementations

---

### kosmos/models/ (5 files)

**Location:** `kosmos/models/`
**Current Coverage:** None
**Lines of Code:** ~800 total
**Impact:** Core Pydantic models for all data structures

#### `models/domain.py`

- **Gap:** No tests for DomainClassification, DomainExpertise models
- **Recommended Tests:**

1. `test_domain_classification_validation` - Verify field validation
2. `test_domain_classification_serialization` - Verify JSON serialization
3. `test_domain_expertise_levels` - Verify expertise enum values

#### `models/experiment.py`

- **Gap:** No tests for ExperimentProtocol validators
- **Recommended Tests:**

1. `test_experiment_protocol_required_fields` - Verify required fields
2. `test_experiment_protocol_duration_validator` - Verify duration format
3. `test_experiment_protocol_cost_validator` - Verify cost bounds
4. `test_experiment_protocol_to_dict` - Verify serialization

#### `models/hypothesis.py`

- **Gap:** No tests for Hypothesis model constraints
- **Recommended Tests:**

1. `test_hypothesis_statement_min_length` - Verify minimum length
2. `test_hypothesis_rationale_required` - Verify rationale
3. `test_hypothesis_confidence_bounds` - Verify 0-1 bounds
4. `test_hypothesis_domain_validation` - Verify domain enum

#### `models/result.py`

- **Gap:** No tests for ExperimentResult model
- **Recommended Tests:**

1. `test_result_status_enum_values` - Verify status enum
2. `test_result_data_serialization` - Verify data handling
3. `test_result_statistics_optional` - Verify optional fields

#### `models/safety.py`

- **Gap:** No tests for SafetyViolation, SafetyReport models - security critical
- **Recommended Tests:**

1. `test_safety_violation_severity_levels` - Verify severity enum
2. `test_safety_report_aggregate_violations` - Verify aggregation
3. `test_approval_request_state_transitions` - Verify states
4. `test_safety_context_required_fields` - Verify context fields

**Mocking Requirements:** None (Pydantic models)

---

### kosmos/api/health.py

**Location:** `kosmos/api/health.py`
**Current Coverage:** None
**Lines of Code:** ~300
**Impact:** System health monitoring

#### `HealthChecker` class

- **Gap:** No tests for health monitoring endpoints
- **Recommended Tests:**

1. `test_health_checker_llm_connectivity` - Verify LLM health check
2. `test_health_checker_database_connectivity` - Verify DB health check
3. `test_health_checker_docker_availability` - Verify Docker check
4. `test_health_checker_redis_connectivity` - Verify Redis check
5. `test_health_checker_neo4j_connectivity` - Verify Neo4j check
6. `test_health_checker_aggregate_status` - Verify aggregate health
7. `test_health_checker_degraded_status` - Verify degraded handling
8. `test_health_checker_unhealthy_status` - Verify unhealthy handling
9. `test_health_checker_timeout_handling` - Verify timeout behavior
10. `test_health_checker_partial_failure` - Verify partial failure

**Mocking Requirements:** Mock all external service connections

---

### kosmos/monitoring/alerts.py

**Location:** `kosmos/monitoring/alerts.py`
**Current Coverage:** None
**Lines of Code:** ~400
**Impact:** Alert management system

#### `AlertManager` class

- **Gap:** No tests for alert creation or notification
- **Recommended Tests:**

1. `test_alert_manager_create_alert` - Verify alert creation
2. `test_alert_manager_alert_severity_levels` - Verify severity handling
3. `test_alert_manager_alert_deduplication` - Verify dedup logic
4. `test_alert_manager_alert_escalation` - Verify escalation rules
5. `test_alert_manager_notification_dispatch` - Verify notification
6. `test_alert_manager_alert_acknowledgment` - Verify acknowledgment
7. `test_alert_manager_alert_resolution` - Verify resolution
8. `test_alert_manager_alert_history` - Verify history tracking
9. `test_alert_manager_rate_limiting` - Verify rate limits
10. `test_alert_manager_silence_rules` - Verify silencing

**Mocking Requirements:** Mock notification backends

---

### kosmos/monitoring/metrics.py (core metrics)

**Location:** `kosmos/monitoring/metrics.py`
**Current Coverage:** None
**Lines of Code:** ~300

- **Gap:** No tests for Prometheus metrics export
- **Recommended Tests:**

1. `test_metrics_prometheus_counter_increment` - Verify counters
2. `test_metrics_prometheus_gauge_set` - Verify gauges
3. `test_metrics_prometheus_histogram_observe` - Verify histograms
4. `test_metrics_prometheus_export_format` - Verify export format

---

## High Priority

These are important functional components with missing or inadequate coverage.

---

### kosmos/core/experiment_cache.py

**Location:** `kosmos/core/experiment_cache.py`
**Current Coverage:** None
**Lines of Code:** ~350

#### `ExperimentCache` class

- **Gap:** No tests for experiment caching and similarity detection
- **Recommended Tests:**

1. `test_experiment_cache_store_result` - Verify storage
2. `test_experiment_cache_get_cached_hit` - Verify cache hit
3. `test_experiment_cache_get_cached_miss` - Verify cache miss
4. `test_experiment_cache_find_similar_above_threshold` - Verify similarity
5. `test_experiment_cache_find_similar_below_threshold` - Verify rejection
6. `test_experiment_cache_fingerprint_generation` - Verify fingerprinting
7. `test_experiment_cache_normalizer` - Verify parameter normalization
8. `test_experiment_cache_stats` - Verify statistics
9. `test_experiment_cache_clear` - Verify clearing
10. `test_experiment_cache_singleton` - Verify singleton

**Mocking Requirements:** Mock SQLite database

---

### kosmos/core/prompts.py

**Location:** `kosmos/core/prompts.py`
**Current Coverage:** None
**Lines of Code:** ~400

#### `PromptTemplate` class and template instances

- **Gap:** No tests for prompt template rendering
- **Recommended Tests:**

1. `test_prompt_template_render_all_variables` - Verify rendering
2. `test_prompt_template_render_missing_variable_raises` - Verify error
3. `test_prompt_template_format_returns_string` - Verify format
4. `test_prompt_template_get_full_prompt_includes_system` - Verify full prompt
5. `test_prompt_hypothesis_generator_template` - Verify HG template
6. `test_prompt_experiment_designer_template` - Verify ED template
7. `test_prompt_data_analyst_template` - Verify DA template
8. `test_prompt_get_template_by_name` - Verify lookup
9. `test_prompt_list_templates_returns_all` - Verify listing

**Mocking Requirements:** None

---

### kosmos/core/providers/base.py

**Location:** `kosmos/core/providers/base.py`
**Current Coverage:** None
**Lines of Code:** ~200

#### `BaseProvider` abstract class

- **Gap:** No tests for provider interface contract
- **Recommended Tests:**

1. `test_base_provider_abstract_methods` - Verify abstract contract
2. `test_base_provider_initialization` - Verify init
3. `test_base_provider_config_validation` - Verify config

---

### kosmos/core/providers/anthropic.py

**Location:** `kosmos/core/providers/anthropic.py`
**Current Coverage:** None
**Lines of Code:** ~300

#### `AnthropicProvider` class

- **Gap:** No tests for Anthropic API integration
- **Recommended Tests:**

1. `test_anthropic_provider_initialization` - Verify init
2. `test_anthropic_provider_complete_success` - Verify completion
3. `test_anthropic_provider_complete_rate_limit` - Verify rate limit handling
4. `test_anthropic_provider_complete_api_error` - Verify error handling
5. `test_anthropic_provider_token_counting` - Verify token counting
6. `test_anthropic_provider_cost_calculation` - Verify cost calc
7. `test_anthropic_provider_timeout_handling` - Verify timeout

**Mocking Requirements:** Mock anthropic.Anthropic client

---

### kosmos/core/providers/openai.py

**Location:** `kosmos/core/providers/openai.py`
**Current Coverage:** None
**Lines of Code:** ~300

#### `OpenAIProvider` class

- **Gap:** No tests for OpenAI API integration
- **Recommended Tests:**

1. `test_openai_provider_initialization` - Verify init
2. `test_openai_provider_complete_success` - Verify completion
3. `test_openai_provider_complete_rate_limit` - Verify rate limit handling
4. `test_openai_provider_complete_api_error` - Verify error handling
5. `test_openai_provider_token_counting` - Verify token counting
6. `test_openai_provider_cost_calculation` - Verify cost calc

**Mocking Requirements:** Mock openai.OpenAI client

---

### kosmos/core/providers/factory.py

**Location:** `kosmos/core/providers/factory.py`
**Current Coverage:** None
**Lines of Code:** ~100

#### `get_provider()` factory function

- **Gap:** No tests for provider factory
- **Recommended Tests:**

1. `test_factory_get_anthropic_provider` - Verify Anthropic creation
2. `test_factory_get_openai_provider` - Verify OpenAI creation
3. `test_factory_get_litellm_provider` - Verify LiteLLM creation
4. `test_factory_invalid_provider_raises` - Verify error handling
5. `test_factory_uses_env_config` - Verify env config

---

### kosmos/world_model/simple.py

**Location:** `kosmos/world_model/simple.py`
**Current Coverage:** None
**Lines of Code:** ~894

#### `Neo4jWorldModel` class

- **Gap:** Production implementation completely untested
- **Recommended Tests:**

1. `test_neo4j_world_model_add_entity_paper` - Verify paper entity
2. `test_neo4j_world_model_add_entity_concept` - Verify concept entity
3. `test_neo4j_world_model_add_entity_author` - Verify author entity
4. `test_neo4j_world_model_get_entity_exists` - Verify retrieval
5. `test_neo4j_world_model_get_entity_not_found` - Verify not found
6. `test_neo4j_world_model_update_entity` - Verify update
7. `test_neo4j_world_model_delete_entity` - Verify deletion
8. `test_neo4j_world_model_add_relationship` - Verify relationship
9. `test_neo4j_world_model_query_related_entities` - Verify traversal
10. `test_neo4j_world_model_export_import_graph` - Verify persistence
11. `test_neo4j_world_model_statistics` - Verify stats
12. `test_neo4j_world_model_verify_entity` - Verify verification
13. `test_neo4j_world_model_annotations` - Verify annotations

**Mocking Requirements:** Mock py2neo Graph connection

---

### kosmos/knowledge/graph_builder.py

**Location:** `kosmos/knowledge/graph_builder.py`
**Current Coverage:** None
**Lines of Code:** ~533

#### `GraphBuilder` class

- **Gap:** Graph construction pipeline untested
- **Recommended Tests:**

1. `test_graph_builder_add_paper_creates_node` - Verify paper node
2. `test_graph_builder_add_paper_extracts_authors` - Verify author extraction
3. `test_graph_builder_build_from_papers_batch` - Verify batch processing
4. `test_graph_builder_extract_concepts_llm` - Verify concept extraction
5. `test_graph_builder_add_citations_creates_edges` - Verify citation edges
6. `test_graph_builder_semantic_relationships` - Verify semantic edges
7. `test_graph_builder_build_stats_tracking` - Verify stats
8. `test_graph_builder_clear_stats` - Verify stats reset

**Mocking Requirements:** Mock KnowledgeGraph, mock ClaudeClient

---

### kosmos/knowledge/graph_visualizer.py

**Location:** `kosmos/knowledge/graph_visualizer.py`
**Current Coverage:** None
**Lines of Code:** ~714

#### `GraphVisualizer` class

- **Gap:** Visualization system untested
- **Recommended Tests:**

1. `test_visualizer_static_generates_matplotlib` - Verify static output
2. `test_visualizer_interactive_generates_html` - Verify interactive output
3. `test_visualizer_citation_network` - Verify citation viz
4. `test_visualizer_concept_network` - Verify concept viz
5. `test_visualizer_author_network` - Verify author viz
6. `test_visualizer_layout_spring` - Verify spring layout
7. `test_visualizer_layout_hierarchical` - Verify hierarchical layout
8. `test_visualizer_layout_circular` - Verify circular layout
9. `test_visualizer_build_networkx_graph` - Verify graph construction

**Mocking Requirements:** Mock matplotlib, mock plotly

---

### kosmos/knowledge/semantic_search.py

**Location:** `kosmos/knowledge/semantic_search.py`
**Current Coverage:** None
**Lines of Code:** ~450

#### `SemanticLiteratureSearch` class

- **Gap:** Search and ranking logic untested
- **Recommended Tests:**

1. `test_semantic_search_returns_ranked_results` - Verify search
2. `test_semantic_search_find_similar_papers` - Verify similarity
3. `test_semantic_search_recommendations` - Verify recommendations
4. `test_semantic_search_build_corpus_index` - Verify indexing
5. `test_semantic_search_corpus_stats` - Verify stats
6. `test_semantic_search_merge_results_dedup` - Verify deduplication
7. `test_semantic_search_rerank_by_similarity` - Verify reranking

**Mocking Requirements:** Mock VectorDB, mock sentence-transformers

---

### kosmos/literature/base_client.py

**Location:** `kosmos/literature/base_client.py`
**Current Coverage:** None
**Lines of Code:** ~300

#### `PaperMetadata`, `Author`, `BaseLiteratureClient`

- **Gap:** Foundation data structures untested
- **Recommended Tests:**

1. `test_paper_metadata_primary_identifier_doi` - Verify DOI priority
2. `test_paper_metadata_primary_identifier_arxiv` - Verify arXiv fallback
3. `test_paper_metadata_author_names_property` - Verify author names
4. `test_paper_metadata_to_dict` - Verify serialization
5. `test_author_dataclass_properties` - Verify author model
6. `test_base_client_validate_query_empty` - Verify empty query
7. `test_base_client_validate_query_too_long` - Verify length limit
8. `test_base_client_handle_api_error` - Verify error handling

**Mocking Requirements:** None

---

### kosmos/literature/cache.py

**Location:** `kosmos/literature/cache.py`
**Current Coverage:** None
**Lines of Code:** ~300

#### `LiteratureCache` class

- **Gap:** Cache system untested
- **Recommended Tests:**

1. `test_literature_cache_generate_key_consistent` - Verify key consistency
2. `test_literature_cache_get_hit` - Verify cache hit
3. `test_literature_cache_get_miss` - Verify cache miss
4. `test_literature_cache_set_stores_data` - Verify storage
5. `test_literature_cache_is_expired_true` - Verify expiration
6. `test_literature_cache_is_expired_false` - Verify not expired
7. `test_literature_cache_invalidate_removes` - Verify invalidation
8. `test_literature_cache_cleanup_expired` - Verify cleanup
9. `test_literature_cache_size_management` - Verify size limits
10. `test_literature_cache_singleton` - Verify singleton

**Mocking Requirements:** Mock filesystem

---

### kosmos/literature/pdf_extractor.py

**Location:** `kosmos/literature/pdf_extractor.py`
**Current Coverage:** None
**Lines of Code:** ~400

#### `PDFExtractor` class

- **Gap:** PDF operations untested
- **Recommended Tests:**

1. `test_pdf_extractor_extract_from_file` - Verify file extraction
2. `test_pdf_extractor_extract_from_url` - Verify URL download
3. `test_pdf_extractor_extract_with_metadata` - Verify metadata
4. `test_pdf_extractor_download_pdf_success` - Verify download
5. `test_pdf_extractor_download_pdf_timeout` - Verify timeout
6. `test_pdf_extractor_download_pdf_404` - Verify 404 handling
7. `test_pdf_extractor_extract_text_pymupdf` - Verify PyMuPDF
8. `test_pdf_extractor_clean_text` - Verify text cleaning
9. `test_pdf_extractor_cache_management` - Verify caching

**Mocking Requirements:** Mock httpx, mock fitz (PyMuPDF)

---

### kosmos/literature/reference_manager.py

**Location:** `kosmos/literature/reference_manager.py`
**Current Coverage:** None
**Lines of Code:** ~500

#### `ReferenceManager`, `DeduplicationEngine` classes

- **Gap:** Reference management untested
- **Recommended Tests:**

1. `test_reference_manager_add_reference` - Verify addition
2. `test_reference_manager_add_references_batch` - Verify batch
3. `test_reference_manager_get_reference` - Verify retrieval
4. `test_reference_manager_search_references` - Verify search
5. `test_reference_manager_deduplicate_by_doi` - Verify DOI dedup
6. `test_reference_manager_deduplicate_by_title` - Verify title dedup
7. `test_reference_manager_comprehensive_dedup` - Verify full dedup
8. `test_reference_manager_merge_duplicates` - Verify merging
9. `test_reference_manager_export_json` - Verify JSON export
10. `test_reference_manager_export_csv` - Verify CSV export
11. `test_dedup_engine_title_similarity` - Verify similarity calc
12. `test_dedup_engine_is_duplicate` - Verify duplicate detection

**Mocking Requirements:** Mock filesystem for storage

---

### kosmos/db/operations.py

**Location:** `kosmos/db/operations.py`
**Current Coverage:** None
**Lines of Code:** ~300

#### Database CRUD operations

- **Gap:** Database operations untested
- **Recommended Tests:**

1. `test_db_create_hypothesis` - Verify hypothesis creation
2. `test_db_get_hypothesis_by_id` - Verify retrieval
3. `test_db_update_hypothesis_status` - Verify status update
4. `test_db_create_experiment` - Verify experiment creation
5. `test_db_get_experiments_for_hypothesis` - Verify query
6. `test_db_create_result` - Verify result creation
7. `test_db_transaction_rollback` - Verify rollback on error
8. `test_db_session_management` - Verify session lifecycle

**Mocking Requirements:** Mock SQLAlchemy session

---

### kosmos/experiments/validator.py

**Location:** `kosmos/experiments/validator.py`
**Current Coverage:** None
**Lines of Code:** ~250

#### `ExperimentValidator` class

- **Gap:** Experiment validation untested
- **Recommended Tests:**

1. `test_validator_validate_protocol_complete` - Verify valid protocol
2. `test_validator_validate_protocol_missing_fields` - Verify rejection
3. `test_validator_validate_constraints_cost` - Verify cost constraints
4. `test_validator_validate_constraints_duration` - Verify duration
5. `test_validator_validate_methodology` - Verify methodology check

---

## Medium Priority

These are functional components with less critical impact but should have coverage.

---

### kosmos/analysis/statistics.py

**Location:** `kosmos/analysis/statistics.py`
**Current Coverage:** None
**Lines of Code:** ~400

- **Gap:** Statistical analysis functions untested
- **Recommended Tests:**

1. `test_statistics_ttest_independent` - Verify t-test
2. `test_statistics_ttest_paired` - Verify paired t-test
3. `test_statistics_anova_one_way` - Verify ANOVA
4. `test_statistics_correlation_pearson` - Verify Pearson
5. `test_statistics_correlation_spearman` - Verify Spearman
6. `test_statistics_regression_linear` - Verify regression
7. `test_statistics_effect_size_cohens_d` - Verify effect size
8. `test_statistics_power_analysis` - Verify power analysis

---

### kosmos/analysis/summarizer.py

**Location:** `kosmos/analysis/summarizer.py`
**Current Coverage:** None
**Lines of Code:** ~300

- **Gap:** Result summarization untested
- **Recommended Tests:**

1. `test_summarizer_summarize_results` - Verify summarization
2. `test_summarizer_extract_key_findings` - Verify finding extraction
3. `test_summarizer_generate_conclusions` - Verify conclusions
4. `test_summarizer_format_for_report` - Verify formatting

---

### kosmos/analysis/plotly_viz.py

**Location:** `kosmos/analysis/plotly_viz.py`
**Current Coverage:** None
**Lines of Code:** ~400

- **Gap:** Plotly visualization untested
- **Recommended Tests:**

1. `test_plotly_scatter_plot` - Verify scatter creation
2. `test_plotly_bar_chart` - Verify bar chart
3. `test_plotly_line_chart` - Verify line chart
4. `test_plotly_heatmap` - Verify heatmap
5. `test_plotly_export_html` - Verify HTML export

---

### kosmos/cli/ (11 untested files)

**Location:** `kosmos/cli/`
**Current Coverage:** 15%

#### Files needing tests:
- `main.py` - Entry point
- `interactive.py` - Interactive mode
- `themes.py` - Theme configuration
- `utils.py` - CLI utilities
- `views/results_viewer.py` - Results display
- `commands/run.py` - Run command
- `commands/config.py` - Config command
- `commands/cache.py` - Cache command
- `commands/history.py` - History command
- `commands/profile.py` - Profile command
- `commands/status.py` - Status command

- **Recommended Tests:** (5 per file, ~55 total)

1. `test_cli_main_entrypoint` - Verify CLI starts
2. `test_cli_run_command_with_objective` - Verify run command
3. `test_cli_config_show` - Verify config display
4. `test_cli_history_list` - Verify history listing
5. `test_cli_status_display` - Verify status

**Mocking Requirements:** Mock click.testing.CliRunner

---

### kosmos/oversight/notifications.py

**Location:** `kosmos/oversight/notifications.py`
**Current Coverage:** None
**Lines of Code:** ~200

- **Gap:** Notification system untested
- **Recommended Tests:**

1. `test_notifications_send_email` - Verify email sending
2. `test_notifications_send_slack` - Verify Slack webhook
3. `test_notifications_queue_notification` - Verify queueing
4. `test_notifications_rate_limiting` - Verify rate limits

---

### kosmos/experiments/templates/ (13 template files)

**Location:** `kosmos/experiments/templates/`
**Current Coverage:** 6%

- **Gap:** Domain-specific templates untested
- **Recommended Tests:**

1. Test each template's `matches()` method
2. Test each template's `generate()` method
3. Test template parameter validation

---

## Low Priority

These are utility or configuration components with lower risk.

---

### kosmos/core/logging.py

**Location:** `kosmos/core/logging.py`
**Current Coverage:** None

- **Gap:** Logging configuration
- **Recommended Tests:**

1. `test_logging_setup_default_level` - Verify default config
2. `test_logging_setup_debug_level` - Verify debug config
3. `test_logging_handlers_configured` - Verify handler setup

---

### kosmos/core/stage_tracker.py

**Location:** `kosmos/core/stage_tracker.py`
**Current Coverage:** None

- **Gap:** Stage tracking for observability
- **Recommended Tests:**

1. `test_stage_tracker_enter_stage` - Verify stage entry
2. `test_stage_tracker_exit_stage` - Verify stage exit
3. `test_stage_tracker_write_jsonl` - Verify output format

---

### kosmos/core/claude_cache.py

**Location:** `kosmos/core/claude_cache.py`
**Current Coverage:** None

- **Gap:** Claude-specific caching
- **Recommended Tests:**

1. `test_claude_cache_prompt_hashing` - Verify hash generation
2. `test_claude_cache_hit_miss` - Verify cache behavior

---

### kosmos/core/profiling.py

**Location:** `kosmos/core/profiling.py`
**Current Coverage:** None

- **Gap:** Performance profiling utilities
- **Recommended Tests:**

1. `test_profiling_timer_context` - Verify timing context
2. `test_profiling_memory_tracking` - Verify memory tracking

---

### kosmos/utils/compat.py

**Location:** `kosmos/utils/compat.py`
**Current Coverage:** None

- **Gap:** Compatibility utilities
- **Recommended Tests:**

1. `test_compat_pydantic_v1_v2` - Verify Pydantic compatibility

---

### kosmos/utils/setup.py

**Location:** `kosmos/utils/setup.py`
**Current Coverage:** None

- **Gap:** Setup utilities
- **Recommended Tests:**

1. `test_setup_database_migration` - Verify migration execution
2. `test_setup_environment_validation` - Verify env checks

---

## Recommendations

### Testing Patterns to Adopt

1. **Use pytest fixtures consistently** - The project uses `conftest.py` but many tests recreate mocks. Centralize common fixtures.

2. **Follow AAA pattern** - Arrange, Act, Assert structure for all tests.

3. **Mock external services at boundaries** - All LLM calls, database operations, and API calls should be mocked.

4. **Use pytest-asyncio for async code** - Many components are async but lack async tests.

5. **Add integration tests for agent communication** - The BaseAgent/AgentRegistry gap means multi-agent flows are untested.

### Suggested Testing Strategy

**Phase 1 (Week 1-2): Critical Infrastructure**
- `agents/base.py` (30 tests)
- `agents/registry.py` (20 tests)
- `execution/jupyter_client.py` (15 tests)
- `execution/parallel.py` (12 tests)
- `core/metrics.py` (13 tests)

**Phase 2 (Week 3-4): High Priority Components**
- `agents/experiment_designer.py` (14 tests)
- `models/` (20 tests)
- `core/providers/` (20 tests)
- `world_model/simple.py` (13 tests)
- `knowledge/` (24 tests)

**Phase 3 (Week 5-6): Medium Priority**
- `literature/` (30 tests)
- `analysis/` (20 tests)
- `api/health.py` (10 tests)
- `monitoring/` (15 tests)

**Phase 4 (Ongoing): Low Priority & Maintenance**
- `cli/` (55 tests)
- `utils/` (5 tests)
- Template files (26 tests)

### Untestable Code Flagged for Refactoring

1. **`execution/jupyter_client.py:_wrap_code()`** - Uses `exec()` indirectly; consider making code execution more modular for easier testing.

2. **`execution/parallel.py:_execute_single_experiment()`** - Module-level function used by ProcessPoolExecutor; difficult to mock. Consider refactoring to use dependency injection.

3. **`cli/interactive.py`** - Heavy use of `input()` and terminal manipulation; needs to be refactored to separate I/O from logic.

4. **`knowledge/graph_visualizer.py`** - Tightly coupled to matplotlib/plotly rendering; consider extracting data preparation from rendering.

---

## Estimated Effort

| Priority | Files | Estimated Tests | Effort (days) |
|----------|-------|-----------------|---------------|
| Critical | 15 | 180 | 8-10 |
| High | 25 | 200 | 10-12 |
| Medium | 20 | 150 | 6-8 |
| Low | 10 | 50 | 2-3 |
| **Total** | **70** | **580** | **26-33** |

---

*Generated by automated test coverage audit*

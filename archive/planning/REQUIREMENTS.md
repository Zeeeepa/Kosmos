# Kosmos AI Scientist - Requirements Specification

**Version:** 1.4 Draft
**Date:** 2025-11-20
**Status:** In Review
**Purpose:** Production readiness validation for Kosmos AI Scientist open-source implementation

---

## Document Scope and Usage

This document defines the complete set of functional, performance, and quality requirements that the Kosmos AI Scientist system MUST, SHOULD, or MAY satisfy to be considered production-ready.

### Requirement Language

This specification uses RFC 2119 key words to indicate requirement levels:

- **MUST / SHALL** = Absolute requirement for production deployment
- **MUST NOT / SHALL NOT** = Absolute prohibition
- **SHOULD / SHOULD NOT** = Strong recommendation, may have justified exceptions
- **MAY** = Optional capability, nice-to-have feature

### Test Coverage Mandate

**REQ-META-001:** Every requirement labeled MUST or SHALL MUST have at least one automated test that validates compliance.

**REQ-META-002:** All tests MUST pass before the system can be considered production-ready.

**REQ-META-003:** Requirements labeled SHOULD SHOULD have automated tests, with documented rationale if test is omitted.

---

## 1. Core Infrastructure Requirements

### 1.1 Execution Environment

**REQ-ENV-001:** The system MUST provide a stable, reproducible execution environment that can be deployed consistently across different host machines.

**REQ-ENV-002:** The system MUST support containerized deployment (Docker or equivalent) for isolation and reproducibility.

**REQ-ENV-003:** The execution environment MUST include all required Python scientific computing libraries (numpy, pandas, scikit-learn) at minimum versions specified in dependencies.

**REQ-ENV-004:** The execution environment MUST include specialized domain libraries for genetic epidemiology (TwoSampleMR, coloc, susieR) as these are required to reproduce key discoveries from the reference implementation. The system SHOULD include gseapy for pathway enrichment analysis.

**REQ-ENV-005:** The system MUST gracefully handle missing optional dependencies without terminating execution.

**REQ-ENV-006:** The execution environment SHOULD include metabolomics processing libraries (xcms, pyopenms, or equivalents) for LC-MS data analysis to support metabolomics research workflows.

**REQ-ENV-007:** The execution environment SHOULD include materials science libraries (pymatgen, ASE, or equivalents) for materials property analysis and crystallographic data processing.

---

### 1.2 LLM Integration

**REQ-LLM-001:** The system MUST establish authenticated connections to configured LLM providers (Anthropic Claude, OpenAI, or compatible endpoints).

**REQ-LLM-002:** The system MUST validate LLM API connectivity during initialization and report connection failures with actionable error messages.

**REQ-LLM-003:** The system MUST implement retry logic with exponential backoff for transient LLM API failures (rate limits, timeouts).

**REQ-LLM-004:** The system MUST handle LLM API errors gracefully without terminating the entire research workflow.

**REQ-LLM-005:** The system MUST parse LLM responses into structured data formats (Pydantic models or equivalent) for downstream processing.

**REQ-LLM-006:** The system MUST distinguish between different LLM output types (natural language, code blocks, structured data) with >95% accuracy.

**REQ-LLM-007:** The system MUST implement prompt caching to reduce API costs for repeated operations during extended 12-hour research cycles. Without prompt caching, the cost of re-processing the growing World Model context for 200+ agent rollouts becomes economically prohibitive.

**REQ-LLM-008:** 🚫 The system MUST NOT expose LLM API keys in logs, error messages, or output artifacts.

**REQ-LLM-009:** 🚫 The system MUST NOT send raw sensitive user data to LLM APIs without sanitization or anonymization.

**REQ-LLM-010:** 🚫 The system MUST NOT use LLM responses as ground truth without validation - responses MUST be verified against domain knowledge or data.

**REQ-LLM-011:** 🚫 The system MUST NOT retry failed LLM API calls indefinitely - a maximum retry limit MUST be enforced.

**REQ-LLM-012:** 🚫 The system MUST NOT expose internal system prompts, reasoning chains, or prompt engineering techniques in user-facing outputs.

---

### 1.3 Configuration Management

**REQ-CFG-001:** The system MUST load configuration from environment variables or configuration files before execution begins.

**REQ-CFG-002:** The system MUST validate all required configuration parameters are present and well-formed before starting a research workflow.

**REQ-CFG-003:** The system MUST provide default values for optional configuration parameters.

**REQ-CFG-004:** The system MUST document all configuration parameters with expected types, valid ranges, and default values.

**REQ-CFG-005:** The system MUST NOT proceed with execution if critical configuration parameters are invalid or missing.

---

### 1.4 Logging and Observability

**REQ-LOG-001:** The system MUST log all significant events (workflow state changes, agent executions, LLM interactions, errors) with timestamps.

**REQ-LOG-002:** The system MUST support configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).

**REQ-LOG-003:** The system MUST write logs to persistent storage that survives process termination.

**REQ-LOG-004:** The system SHOULD structure logs in machine-parseable format (JSON or equivalent) for automated analysis.

**REQ-LOG-005:** The system MUST NOT log sensitive information (API keys, credentials, personally identifiable data) at any log level.

**REQ-LOG-006:** The system MUST provide correlation IDs to trace related events across components and iterations.

---

## 2. Data Analysis Agent Requirements

### 2.1 Code Generation

**REQ-DAA-GEN-001:** The Data Analysis Agent MUST generate syntactically valid Python or R code for specified analysis tasks with >95% success rate.

**REQ-DAA-GEN-002:** The generated code MUST be executable in the configured sandbox environment without manual modification.

**REQ-DAA-GEN-003:** The Data Analysis Agent MUST generate code that directly addresses the specified analysis objective (validated by human review or automated metrics).

**REQ-DAA-GEN-004:** The generated code SHOULD include comments explaining key analytical steps.

**REQ-DAA-GEN-005:** 🚫 The Data Analysis Agent MUST NOT generate code containing hard-coded credentials, absolute file paths, or non-portable system calls.

**REQ-DAA-GEN-006:** 🚫 The system MUST NOT execute code that uses `eval()` or `exec()` on untrusted input or user-provided strings.

**REQ-DAA-GEN-007:** 🚫 The Data Analysis Agent MUST NOT generate code that modifies global state or environment variables that could affect other components.

---

### 2.2 Code Execution

**REQ-DAA-EXEC-001:** The system MUST execute agent-generated code in an isolated sandbox environment that prevents access to the host system.

**REQ-DAA-EXEC-002:** The sandbox environment MUST capture stdout, stderr, and generated artifacts (plots, tables) from code execution.

**REQ-DAA-EXEC-003:** The sandbox execution MUST enforce resource limits (CPU time, memory, disk I/O) to prevent runaway processes.

**REQ-DAA-EXEC-004:** The system MUST terminate code execution that exceeds configured timeout limits and log the timeout event.

**REQ-DAA-EXEC-005:** The system MUST capture and report execution errors (syntax errors, runtime exceptions) with stack traces for debugging.

**REQ-DAA-EXEC-006:** The system MUST measure and record execution time for all code runs.

**REQ-DAA-EXEC-007:** The sandbox MUST provide read-only access to the input dataset without allowing modification.

**REQ-DAA-EXEC-008:** The system MAY support both containerized (Docker) and direct execution modes for testing and development.

**REQ-DAA-EXEC-009:** 🚫 The sandbox MUST NOT allow code to execute arbitrary shell commands. Spawning subprocesses SHOULD be restricted to a predefined allowlist of safe scientific tools required for domain analysis (e.g., statistical genetics tools that wrap R executables).

**REQ-DAA-EXEC-010:** 🚫 The sandbox MUST NOT allow code to modify system environment variables visible to other processes.

**REQ-DAA-EXEC-011:** 🚫 The system MUST NOT proceed with code execution if the sandbox initialization fails or is unavailable (when sandboxing is required).

**REQ-DAA-EXEC-012:** The Data Analysis Agent SHOULD implement a self-correction loop that analyzes stderr output and regenerates code when execution fails, with a maximum of 3 retry attempts per task.

---

### 2.3 Analysis Capabilities

**REQ-DAA-CAP-001:** The Data Analysis Agent MUST successfully perform exploratory data analysis (summary statistics, distributions, missing value analysis).

**REQ-DAA-CAP-002:** The Data Analysis Agent MUST successfully perform data transformations (normalization, log transformation, scaling).

**REQ-DAA-CAP-003:** The Data Analysis Agent MUST successfully perform statistical tests (t-tests, ANOVA, chi-square, correlation analysis).

**REQ-DAA-CAP-004:** The Data Analysis Agent MUST successfully perform regression analysis (linear, logistic, multivariate).

**REQ-DAA-CAP-005:** The Data Analysis Agent MUST successfully perform advanced analyses (feature importance via SHAP, distribution fitting, segmented regression) as these methods are critical for reproducing paper discoveries.

**REQ-DAA-CAP-006:** The Data Analysis Agent MUST successfully generate publication-quality visualizations (scatter plots, box plots, heatmaps, distribution plots) as the paper's discoveries rely heavily on generated visualizations.

**REQ-DAA-CAP-007:** The system MUST validate analysis outputs for statistical validity (e.g., p-values in valid range, confidence intervals properly calculated).

**REQ-DAA-CAP-008:** The Data Analysis Agent MUST successfully perform pathway enrichment analysis using standard biological databases and tools (e.g., gseapy), as this capability was essential for multiple discoveries highlighted in the paper (Discoveries 1 and 6).

**REQ-DAA-CAP-009:** The Data Analysis Agent SHOULD be capable of defining novel composite metrics or proposing unconventional analytical methods relevant to the research objective (e.g., Mechanistic Ranking Score in Discovery 5, applying segmented regression in novel contexts), demonstrating advanced analytical autonomy.

---

### 2.4 Result Summarization and Artifacts

**REQ-DAA-SUM-001:** The Data Analysis Agent MUST generate natural language summaries of analysis results that are scientifically accurate.

**REQ-DAA-SUM-002:** The summary MUST include key statistical findings (test statistics, p-values, effect sizes) when applicable.

**REQ-DAA-SUM-003:** The system MUST serialize complete analysis sessions (code + output + summary) into reproducible artifacts.

**REQ-DAA-SUM-004:** Artifacts MUST be stored in executable notebook format (Jupyter .ipynb or equivalent) for human review and traceability, as the paper states "each statement cites a Jupyter notebook."

**REQ-DAA-SUM-005:** The system MUST assign unique, persistent identifiers to all generated artifacts.

---

### 2.5 Safety and Validation

**REQ-DAA-SAFE-001:** The system MUST validate all generated code for dangerous operations (file system access, network calls, subprocess execution) before execution.

**REQ-DAA-SAFE-002:** The code validator MUST use AST-based static analysis to detect prohibited operations with >99% recall.

**REQ-DAA-SAFE-003:** The system MUST block execution of code containing prohibited operations and log the violation.

**REQ-DAA-SAFE-004:** 🚫 The system MUST NOT execute code that attempts to import unauthorized modules (e.g., `os.system`, `subprocess`, `socket`).

**REQ-DAA-SAFE-005:** The safety validator MUST provide detailed violation reports indicating the specific prohibited operation and its location in the code.

**REQ-DAA-SAFE-006:** 🚫 The system MUST NOT allow code to access or modify files outside the designated data and output directories.

**REQ-DAA-SAFE-007:** 🚫 The system MUST NOT execute code containing infinite loops or recursion without depth limits (detected via static analysis where possible).

**REQ-DAA-SAFE-008:** Data analysis statements in generated reports SHOULD achieve ≥85% reproducibility rate when independently validated.

**REQ-DAA-SAFE-009:** Literature review statements in generated reports SHOULD achieve ≥82% validation rate when checked against cited sources.

**REQ-DAA-SAFE-010:** Synthesis and interpretation statements SHOULD be flagged as lower-confidence claims requiring human validation (target accuracy: ~58%).

**REQ-DAA-SAFE-011:** Overall statement accuracy across all report types SHALL target ≥79% when validated by domain experts.

---

## 3. Literature Search Agent Requirements

**REQ-LSA-001:** The Literature Search Agent MUST translate research tasks into effective search queries for external knowledge sources.

**REQ-LSA-002:** The system MUST successfully connect to at least one literature database (PubMed, Semantic Scholar, or equivalent).

**REQ-LSA-003:** The Literature Search Agent MUST attempt to retrieve full-text articles when available, falling back to abstracts only when full text is unavailable, as the paper emphasizes reading "1,500 full-length scientific papers" per run.

**REQ-LSA-004:** The system MUST parse retrieved documents (PDF, HTML, XML) into machine-readable text with >90% content preservation.

**REQ-LSA-005:** The Literature Search Agent MUST synthesize information from multiple retrieved papers into coherent knowledge summaries.

**REQ-LSA-006:** The system MUST cite primary sources for all synthesized information with retrievable identifiers (DOI, PMID, arXiv ID).

**REQ-LSA-007:** The Literature Search Agent SHOULD validate the recency of retrieved literature and prefer recent publications when multiple sources are available.

**REQ-LSA-008:** The system MAY implement local caching of retrieved literature to reduce API calls and costs.

**REQ-LSA-009:** The system MUST handle literature API failures gracefully and continue the workflow with available information.

**REQ-LSA-010:** 🚫 The Literature Search Agent MUST NOT cite retracted papers or papers flagged for scientific misconduct.

**REQ-LSA-011:** 🚫 The system MUST NOT rely solely on non-peer-reviewed sources (preprints, blog posts) as primary evidence for scientific claims.

**REQ-LSA-012:** 🚫 The Literature Search Agent MUST NOT synthesize contradictory findings without explicitly noting the conflict and uncertainty.

**REQ-LSA-013:** The Literature Search Agent SHALL process and index a minimum of 125 papers per hour to support the documented capability of reading 1,500 papers within a 12-hour research cycle.

---

## 4. Structured World Model Requirements

### 4.1 Data Model and Schema

**REQ-WM-SCHEMA-001:** The World Model MUST enforce a defined schema for storing hypotheses, analysis results, literature findings, and their relationships.

**REQ-WM-SCHEMA-002:** The schema MUST support versioning to track evolution of knowledge over iterations.

**REQ-WM-SCHEMA-003:** The World Model MUST maintain referential integrity between related entities (hypotheses → experiments → results).

**REQ-WM-SCHEMA-004:** The system MUST validate all data against the schema before insertion to prevent corruption.

**REQ-WM-SCHEMA-005:** The structured world model SHALL store entities, relationships, experimental results, and open questions as distinct, queryable data types with appropriate schema definitions.

**REQ-WM-SCHEMA-006:** The world model SHALL be updated after every task execution to ensure all agents have access to the latest research state.

---

### 4.2 CRUD Operations

**REQ-WM-CRUD-001:** The World Model MUST support creating new entities (hypotheses, results, literature summaries) with all required fields.

**REQ-WM-CRUD-002:** The World Model MUST support reading entities by unique identifier with <100ms latency for 90th percentile queries.

**REQ-WM-CRUD-003:** The World Model MUST support updating existing entities while preserving version history.

**REQ-WM-CRUD-004:** The World Model SHOULD support deleting entities (with confirmation for safety).

**REQ-WM-CRUD-005:** All CRUD operations MUST maintain ACID properties (Atomicity, Consistency, Isolation, Durability) when using transactional storage.

**REQ-WM-CRUD-006:** 🚫 The World Model MUST NOT allow deletion of entities that have active references from other entities without cascading or explicit conflict resolution.

**REQ-WM-CRUD-007:** 🚫 The system MUST NOT accept updates that would break referential integrity between entities.

---

### 4.3 Querying and Context Retrieval

**REQ-WM-QUERY-001:** The World Model MUST support complex queries to retrieve context for task planning (e.g., "all hypotheses related to gene X").

**REQ-WM-QUERY-002:** The query mechanism MUST return results ranked by relevance to the current research context.

**REQ-WM-QUERY-003:** The World Model MUST support filtering by metadata (domain, status, iteration number, timestamp).

**REQ-WM-QUERY-004:** The system MUST retrieve the complete context for a given workflow state in <1 second for databases up to 10,000 entities.

---

### 4.4 Concurrency and Data Integrity

**REQ-WM-CONC-001:** The World Model MUST handle concurrent read operations from multiple agents without data corruption.

**REQ-WM-CONC-002:** The World Model MUST serialize write operations to prevent race conditions when multiple agents update simultaneously.

**REQ-WM-CONC-003:** The system MUST implement optimistic or pessimistic locking to handle concurrent updates to the same entity.

**REQ-WM-CONC-004:** The World Model MUST detect and report deadlock conditions if they occur during concurrent operations.

**REQ-WM-CONC-005:** The World Model SHALL support queries from up to 200 concurrent agent rollouts without performance degradation or data corruption.

---

### 4.5 Persistence and Backup

**REQ-WM-PERSIST-001:** The World Model MUST persist all data to durable storage (database, file system) that survives process restarts.

**REQ-WM-PERSIST-002:** The system SHOULD support periodic snapshots of the World Model state for backup and recovery.

**REQ-WM-PERSIST-003:** The system MUST support exporting the complete World Model in a portable format (JSON, SQL dump).

**REQ-WM-PERSIST-004:** The system MUST support importing a previously exported World Model to resume or replicate research.

**REQ-WM-PERSIST-005:** 🚫 The system MUST NOT allow retroactive modification of provenance records or historical entity states.

**REQ-WM-PERSIST-006:** 🚫 The World Model MUST NOT merge conflicting information from different sources without explicit conflict resolution and documentation.

---

## 5. Orchestrator (Research Director) Requirements

### 5.1 Discovery Cycle Architecture

**REQ-ORCH-CYCLE-001:** The Orchestrator MUST implement a structured seven-phase discovery cycle that guides the research process: (1) Literature Search → (2) Hypothesis Generation → (3) Experiment Design → (4) Execution → (5) Analysis → (6) Refinement → (7) Convergence. This cycle structure enables coherent pursuit of research objectives across 200+ agent rollouts.

**REQ-ORCH-SYN-001:** The Orchestrator MUST implement a synthesis mechanism that integrates findings from the World Model to generate novel, testable scientific hypotheses and propose strategic tasks for the next iteration. This mechanism is responsible for the intelligent planning that differentiates autonomous discovery from random exploration.

---

### 5.2 Workflow Lifecycle Management

**REQ-ORCH-LIFE-001:** The Orchestrator MUST successfully initialize a research workflow from a research question and dataset.

**REQ-ORCH-LIFE-002:** The Orchestrator MUST manage the complete lifecycle: Initialization → Task Planning → Agent Execution → Result Integration → World Model Update → Iteration.

**REQ-ORCH-LIFE-003:** The Orchestrator SHOULD support pausing and resuming workflows without loss of state (feature not described in research paper).

**REQ-ORCH-LIFE-004:** The Orchestrator MUST detect workflow completion conditions (convergence, iteration limit, time limit, budget exhausted).

**REQ-ORCH-LIFE-005:** The Orchestrator MUST gracefully terminate workflows when termination conditions are met.

---

### 5.3 Task Planning and Dispatch

**REQ-ORCH-TASK-001:** The Orchestrator MUST query the World Model to retrieve context for planning new tasks.

**REQ-ORCH-TASK-002:** The Orchestrator MUST generate task specifications that include clear objectives, input data references, and success criteria.

**REQ-ORCH-TASK-003:** The Orchestrator MUST dispatch tasks to appropriate agents (Data Analysis Agent for analysis tasks, Literature Search Agent for knowledge retrieval).

**REQ-ORCH-TASK-004:** The Orchestrator SHOULD support parallel execution of independent tasks up to a configured maximum concurrency limit.

**REQ-ORCH-TASK-005:** The Orchestrator MUST track the status of all dispatched tasks (pending, running, completed, failed).

**REQ-ORCH-TASK-006:** The Orchestrator MUST enforce timeout limits on agent tasks and handle timeouts appropriately.

**REQ-ORCH-TASK-007:** The Orchestrator SHALL support a configurable maximum parallel task limit with a default of 10 concurrent tasks as demonstrated in the reference implementation.

---

### 5.4 Iteration and Convergence

**REQ-ORCH-ITER-001:** The Orchestrator MUST support multi-iteration research cycles where each iteration builds on previous results.

**REQ-ORCH-ITER-002:** The Orchestrator MUST demonstrate cross-cycle coherence: information from iteration N MUST inform task planning in iteration N+1.

**REQ-ORCH-ITER-003:** The Orchestrator MUST track iteration count and enforce maximum iteration limits.

**REQ-ORCH-ITER-004:** The Orchestrator MUST implement convergence detection based on diminishing new discoveries or hypothesis confidence to enable autonomous termination as described in "once Kosmos believes it has completed the research objective."

**REQ-ORCH-ITER-005:** The Orchestrator MUST log the reason for workflow termination (convergence, iteration limit, error, manual stop).

**REQ-ORCH-ITER-006:** 🚫 The Orchestrator MUST NOT allow infinite iteration loops - a hard maximum iteration limit MUST be enforced.

**REQ-ORCH-ITER-007:** 🚫 The Orchestrator MUST NOT proceed to the next iteration if the World Model state is inconsistent or corrupted.

**REQ-ORCH-ITER-008:** The Orchestrator SHALL allow manual override of automatic convergence detection to enable human-directed early termination or continuation beyond detected convergence.

---

### 5.5 Error Handling and Recovery

**REQ-ORCH-ERR-001:** The Orchestrator MUST handle individual agent failures without terminating the entire workflow.

**REQ-ORCH-ERR-002:** The Orchestrator MUST log all agent failures with sufficient context for debugging (task specification, error message, stack trace).

**REQ-ORCH-ERR-003:** The Orchestrator SHOULD attempt task retry for transient failures (up to configured retry limit).

**REQ-ORCH-ERR-004:** The Orchestrator MAY implement adaptive strategies when repeated failures occur (e.g., simplify task, try alternative approach).

**REQ-ORCH-ERR-005:** 🚫 The Orchestrator MUST NOT retry tasks that fail due to safety violations.

**REQ-ORCH-ERR-006:** 🚫 The Orchestrator MUST NOT ignore critical errors - only transient failures (network timeouts, rate limits) MAY be retried.

**REQ-ORCH-ERR-007:** 🚫 The system MUST NOT execute contradictory or mutually exclusive tasks simultaneously.

**REQ-ORCH-ERR-008:** When an analysis task fails for technical reasons (e.g., tool unavailability, data incompatibility), the Orchestrator SHOULD attempt to identify and execute alternative analytical approaches to achieve the task objective, demonstrating analytical resilience as shown in the paper's Discovery 4 (pivoting from colocalization to SuSiE fine-mapping).

---

### 5.6 Resource Management

**REQ-ORCH-RES-001:** The Orchestrator MUST track API usage (LLM calls, literature API calls) and enforce budget limits.

**REQ-ORCH-RES-002:** The Orchestrator MUST monitor computational resource usage (CPU time, memory) and respect configured limits.

**REQ-ORCH-RES-003:** The Orchestrator MUST terminate workflows that exceed configured resource budgets (API cost, computation time).

**REQ-ORCH-RES-004:** The system SHOULD provide real-time resource usage metrics during execution.

---

## 6. Integration and Coordination Requirements

### 6.1 Agent-World Model Integration

**REQ-INT-AWM-001:** Agent result summaries MUST be successfully ingested into the World Model without data loss.

**REQ-INT-AWM-002:** The system MUST link agent-generated artifacts to their corresponding World Model entries via unique identifiers.

**REQ-INT-AWM-003:** The system MUST handle schema mismatches between agent outputs and World Model expectations gracefully.

---

### 6.2 Cross-Agent Coordination

**REQ-INT-CROSS-001:** Information discovered by the Literature Search Agent MUST be accessible to the Data Analysis Agent via the World Model.

**REQ-INT-CROSS-002:** Hypotheses generated by one agent MAY trigger tasks for other agents in subsequent iterations.

**REQ-INT-CROSS-003:** The system MUST prevent circular dependencies between agent tasks that could cause deadlocks.

---

### 6.3 Parallel Execution

**REQ-INT-PAR-001:** The system MUST support executing up to 10 independent agent tasks in parallel per discovery cycle, as explicitly stated in the paper: "In each cycle, Kosmos executes up to ten literature search and analysis tasks."

**REQ-INT-PAR-002:** Parallel execution MUST NOT cause data corruption in the World Model.

**REQ-INT-PAR-003:** The system MUST provide fair resource allocation among parallel tasks (no starvation).

**REQ-INT-PAR-004:** The system MUST complete all parallel tasks in an iteration before proceeding to the next iteration.

---

## 7. Output and Traceability Requirements

### 7.1 Artifact Management

**REQ-OUT-ART-001:** The system MUST store all generated artifacts (code, notebooks, visualizations, logs) in a centralized, accessible location.

**REQ-OUT-ART-002:** Artifacts MUST be organized by workflow run, iteration, and agent for easy navigation.

**REQ-OUT-ART-003:** The system MUST preserve artifacts for the lifetime of the research workflow and beyond (configurable retention period).

**REQ-OUT-ART-004:** The system SHOULD support artifact export for external archival or publication.

---

### 7.2 Provenance and Citations

**REQ-OUT-PROV-001:** Every entity in the World Model MUST have a provenance record linking it to the agent execution that created it.

**REQ-OUT-PROV-002:** The provenance record MUST include: artifact ID, timestamp, agent type, input data, and execution parameters.

**REQ-OUT-PROV-003:** The system MUST support querying provenance to trace any finding back to its source artifact.

**REQ-OUT-PROV-004:** The final report MUST cite the source artifact for every factual claim, figure, or conclusion.

**REQ-OUT-PROV-005:** All citations MUST resolve to accessible artifacts (hyperlinks, file paths, or retrievable identifiers).

---

### 7.3 Report Generation

**REQ-OUT-RPT-001:** The system MUST generate one or more scientific reports summarizing the workflow's discoveries, with support for multiple discovery narratives within or across reports as described in the paper's "three or four scientific reports" output.

**REQ-OUT-RPT-002:** The report MUST include sections for: research objective, hypotheses generated, analyses performed, key findings, and conclusions.

**REQ-OUT-RPT-003:** The report MUST embed or link to all supporting figures and tables generated during the workflow.

**REQ-OUT-RPT-004:** The report SHOULD be generated in a publication-ready format (Markdown, PDF, or LaTeX).

**REQ-OUT-RPT-005:** The report MUST include a complete provenance section mapping all claims to source artifacts.

**REQ-OUT-RPT-006:** The system MUST support generating 3-4 distinct scientific reports from a single research workflow, each focusing on a coherent discovery narrative as demonstrated in the paper.

**REQ-OUT-RPT-007:** Each discovery narrative in a report SHOULD contain approximately 25 factual claims based on 8-9 agent trajectories, providing appropriate depth and evidence backing.

**REQ-OUT-RPT-008:** Each discovery narrative SHOULD reference 5-10 distinct agent trajectories as supporting evidence to ensure findings are well-substantiated.

**REQ-OUT-RPT-009:** Discovery narratives SHOULD contain 20-30 factual claims with complete provenance to source trajectories, balancing comprehensiveness with readability.

---

### 7.4 Discovery Narrative Identification

**REQ-OUT-DISC-001:** The system MUST implement a mechanism to identify distinct, coherent discovery narratives from the accumulated findings in the Structured World Model, enabling the synthesis of focused discovery reports.

---

### 7.5 Statement Classification

**REQ-OUT-CLASS-001:** The system MUST classify each claim in generated reports into one of three categories: (1) data analysis-derived, (2) literature-derived, or (3) interpretation/synthesis, as these categories have different accuracy characteristics.

**REQ-OUT-CLASS-002:** Report provenance MUST indicate the statement type for each claim to enable type-specific accuracy validation as performed in the paper's evaluation (85.5% for data analysis, 82.1% for literature, 57.9% for interpretation).

---

## 8. Domain and Data Requirements

### 8.1 Multi-Domain Support

**REQ-DOMAIN-001:** The system MUST successfully execute research workflows in at least three scientific domains (biology, neuroscience, physics, chemistry, or materials science).

**REQ-DOMAIN-002:** The system MUST NOT require domain-specific code modifications to handle different domains (configuration only).

**REQ-DOMAIN-003:** The system SHOULD provide domain-specific prompt templates or knowledge bases to improve analysis quality.

---

### 8.2 Dataset Handling

**REQ-DATA-001:** The system MUST support datasets up to 5GB in size (as mentioned in paper limitations).

**REQ-DATA-002:** The system MUST support common data formats (CSV, JSON, Parquet, HDF5).

**REQ-DATA-003:** The system MUST validate dataset schema and data types before beginning analysis.

**REQ-DATA-004:** The system SHOULD provide automated data quality checks (missing values, outliers, distribution shifts).

**REQ-DATA-005:** The system MUST handle missing or malformed data gracefully without crashing.

**REQ-DATA-006:** 🚫 The system MUST NOT modify or overwrite original input datasets - all transformations MUST create new derived datasets.

**REQ-DATA-007:** 🚫 The system MUST NOT proceed with analysis if data quality checks reveal critical issues (>50% missing values, schema mismatches, data type inconsistencies).

**REQ-DATA-008:** 🚫 The system MUST NOT mix data from different research domains or experiments without explicit user instruction and clear provenance tracking.

**REQ-DATA-009:** 🚫 The system MUST NOT accept datasets without clear provenance information (source, collection date, data dictionary).

**REQ-DATA-010:** 🚫 The system MUST NOT claim to support datasets larger than 5GB - this is a known system limitation.

**REQ-DATA-011:** The system SHALL validate dataset size before processing and reject datasets exceeding 5GB with a clear error message explaining the limitation.

**REQ-DATA-012:** 🚫 The system MUST NOT process raw image data or raw sequencing files - only preprocessed, structured data formats are supported.

---

## 9. Performance and Scalability Requirements

### 9.1 Stability and Reliability

**REQ-PERF-STAB-001:** The system MUST remain stable over extended runtimes up to 12 hours without memory leaks or resource exhaustion.

**REQ-PERF-STAB-002:** The system MUST successfully complete workflows with up to 20 iterations.

**REQ-PERF-STAB-003:** The system MUST handle at least 200 agent rollouts (executions) per workflow without performance degradation, as the paper demonstrates an average of 202 rollouts (166 data analysis + 36 literature).

**REQ-PERF-STAB-004:** The system SHOULD maintain high stability during workflow execution (excluding external API failures). Note: Kosmos is a batch research process, not a continuously available service requiring uptime SLAs.

---

### 9.2 Response Times

**REQ-PERF-TIME-001:** The system SHOULD generate initial hypotheses within 5 minutes of workflow initiation.

**REQ-PERF-TIME-002:** The system SHOULD complete a single iteration (task planning → execution → integration) in <30 minutes for datasets <1GB.

**REQ-PERF-TIME-003:** World Model queries MUST return results in <1 second for 90th percentile queries.

---

### 9.3 Resource Efficiency

**REQ-PERF-RES-001:** The system SHOULD leverage prompt caching to reduce redundant LLM API calls by >50% for repeated prompts.

**REQ-PERF-RES-002:** The system SHOULD parallelize independent tasks to reduce total workflow time compared to sequential execution.

**REQ-PERF-RES-003:** The system MUST operate within configured memory limits (default: 8GB RAM per agent).

**REQ-PERF-RES-004:** 🚫 The system MUST NOT block the entire workflow waiting for slow external API calls - timeouts MUST be enforced.

**REQ-PERF-RES-005:** 🚫 The system MUST NOT load entire large datasets (>1GB) into memory if streaming or chunked processing is feasible.

**REQ-PERF-RES-006:** 🚫 The system MUST NOT execute analyses with exponential time complexity (O(2^n) or worse) on datasets with n > 1000 elements without user confirmation.

**REQ-PERF-RES-007:** The system SHOULD track and report lines of code executed per research cycle for performance benchmarking.

**REQ-PERF-RES-008:** The system SHOULD track and report number of papers read per research cycle for performance benchmarking.

**REQ-PERF-RES-009:** The system SHOULD track and report agent rollout counts (data analysis, literature review) per research cycle for performance benchmarking.

**REQ-PERF-SCALE-001:** The system MUST demonstrate the capability to execute at least 40,000 lines of code across multiple agent rollouts in a single research workflow, as demonstrated in the paper with an average of 42,000 lines.

**REQ-PERF-SCALE-002:** The system MUST demonstrate the capability to process at least 1,000 full-text scientific papers in a single research workflow, as demonstrated in the paper with an average of 1,500 papers.

**REQ-PERF-SCALE-003:** The system MUST support at least 150 data analysis agent rollouts per workflow without performance degradation, as demonstrated in the paper with an average of 166 rollouts.

---

## 10. Scientific Validity Requirements

### 10.1 Hypothesis Quality

**REQ-SCI-HYP-001:** Generated hypotheses MUST be scientifically testable (validated by human expert review).

**REQ-SCI-HYP-002:** Generated hypotheses MUST be relevant to the research question (semantic similarity >0.7).

**REQ-SCI-HYP-003:** Generated hypotheses SHOULD be novel (not directly found in training data or retrieved literature).

**REQ-SCI-HYP-004:** Hypotheses MUST include clear rationale explaining the scientific reasoning.

**REQ-SCI-HYP-005:** 🚫 The system MUST NOT generate hypotheses that contradict established physical laws or well-validated scientific principles without explicit justification.

**REQ-SCI-HYP-006:** 🚫 The system MUST NOT claim causation from correlation without experimental design that controls for confounding variables.

---

### 10.2 Analysis Validity

**REQ-SCI-ANA-001:** Statistical analyses MUST use appropriate methods for the data type and distribution.

**REQ-SCI-ANA-002:** The system MUST check statistical assumptions (normality, independence, homoscedasticity) before applying parametric tests.

**REQ-SCI-ANA-003:** The system SHOULD report effect sizes alongside p-values for all statistical tests.

**REQ-SCI-ANA-004:** The system MUST flag analyses that violate assumptions and suggest alternative approaches.

**REQ-SCI-ANA-005:** 🚫 The system MUST NOT perform statistical tests on data that grossly violates test assumptions (e.g., t-test on heavily skewed non-normal data with small n).

**REQ-SCI-ANA-006:** 🚫 The system MUST report effect sizes alongside p-values, and SHOULD report confidence intervals when applicable. Note: The paper itself reports p-values without CIs in some visualizations.

**REQ-SCI-ANA-007:** 🚫 The system MUST NOT cherry-pick analyses or report only statistically significant results - all performed analyses MUST be documented.

---

### 10.3 Reproducibility

**REQ-SCI-REPRO-001:** All analyses MUST be reproducible from stored artifacts (same code + same data → same results).

**REQ-SCI-REPRO-002:** The system MUST record all random seeds and parameters used in stochastic analyses.

**REQ-SCI-REPRO-003:** The system MUST version-lock all software dependencies to ensure long-term reproducibility.

**REQ-SCI-REPRO-004:** Artifacts SHOULD include environment specifications (container image, dependency manifest) for exact reproduction.

**REQ-SCI-REPRO-005:** 🚫 The system MUST NOT guarantee deterministic results across multiple runs with identical inputs - the discovery process is inherently stochastic.

**REQ-SCI-REPRO-006:** The system SHALL document that multiple runs with identical inputs may produce different discoveries due to stochastic LLM responses and non-deterministic search strategies.

**REQ-SCI-REPRO-007:** The system SHOULD provide variance and confidence metrics when multiple runs with identical inputs are executed for research validation.

---

### 10.4 Validation Against Ground Truth

**REQ-SCI-VAL-001:** The system SHOULD be tested against known scientific discoveries to validate discovery capability.

**REQ-SCI-VAL-002:** When tested on benchmark problems, the system SHOULD reach scientifically correct conclusions >80% of the time.

**REQ-SCI-VAL-004:** When evaluated by domain experts, the system MUST achieve >75% overall accuracy across all statement types in generated reports, based on the paper's demonstrated 79.4% overall accuracy.

**REQ-SCI-VAL-005:** Data analysis-based statements MUST achieve >80% accuracy when independently validated by domain experts, based on the paper's demonstrated 85.5% accuracy for data analysis statements.

**REQ-SCI-VAL-006:** Literature review-based statements MUST achieve >75% accuracy when validated against primary sources, based on the paper's demonstrated 82.1% accuracy for literature statements.

**REQ-SCI-VAL-007:** The system MUST track accuracy by statement type (data analysis, literature synthesis, interpretation) and report these metrics separately, as interpretation statements are expected to have lower accuracy (~58%) compared to data analysis or literature statements.

---

### 10.5 Performance Metrics and Benchmarking

**REQ-SCI-METRIC-001:** The system SHOULD provide metrics estimating the equivalent expert time represented by the work performed (e.g., papers read × 15 minutes/paper + analyses × 2 hours/analysis), as the paper reports Kosmos performs work equivalent to 6 months of expert time.

**REQ-SCI-METRIC-002:** The system SHOULD track the cumulative expert-equivalent time across discovery iterations to demonstrate scaling of research output with runtime.

**REQ-SCI-EVAL-001:** The system SHOULD provide mechanisms for assessing the novelty of generated findings (e.g., comparing against training data cutoff, literature corpus) as the paper evaluates discoveries on moderate to complete novelty.

**REQ-SCI-EVAL-002:** The system SHOULD provide mechanisms for assessing the reasoning depth of generated findings (e.g., number of inferential steps, cross-domain synthesis) as the paper evaluates discoveries on high to moderate reasoning depth.

---

## 11. Security and Safety Requirements

### 11.1 Code Execution Safety

**REQ-SEC-EXEC-001:** Generated code MUST execute in an isolated sandbox with no access to host file system (except designated data directories).

**REQ-SEC-EXEC-002:** Generated code MUST NOT be able to access network resources unless explicitly permitted.

**REQ-SEC-EXEC-003:** Generated code MUST NOT be able to execute arbitrary system commands.

**REQ-SEC-EXEC-004:** The sandbox MUST enforce resource limits to prevent denial-of-service (CPU, memory, disk, execution time).

---

### 11.2 Data Privacy and Security

**REQ-SEC-DATA-001:** The system MUST NOT expose sensitive data (credentials, API keys, personal information) in logs or outputs.

**REQ-SEC-DATA-002:** The system SHOULD support data anonymization for sensitive datasets before analysis.

**REQ-SEC-DATA-003:** Artifacts containing sensitive data SHOULD be encrypted at rest.

**REQ-SEC-DATA-004:** The system SHOULD comply with applicable data protection regulations (GDPR, HIPAA if handling relevant data) when deployed in production environments. Note: Regulatory compliance is a deployment concern not specified in the research paper.

---

### 11.3 API and External Access

**REQ-SEC-API-001:** API credentials MUST be stored securely (environment variables, secret management system) and never hard-coded.

**REQ-SEC-API-002:** The system MUST implement rate limiting to prevent accidental API abuse.

**REQ-SEC-API-003:** The system SHOULD validate all external API responses for malicious content before processing.

**REQ-SEC-API-004:** 🚫 The system MUST NOT send user data or research data to external APIs without explicit user consent and disclosure.

**REQ-SEC-API-005:** 🚫 The system MUST NOT cache sensitive API responses (containing credentials, personal data) in plaintext.

---

## 12. Testing and Validation Requirements

### 12.1 Test Coverage

**REQ-TEST-COV-001:** The system MUST have automated tests covering >80% of core functionality code paths.

**REQ-TEST-COV-002:** All requirements labeled MUST or SHALL MUST have at least one automated test validating compliance.

**REQ-TEST-COV-003:** The test suite MUST include unit tests, integration tests, and end-to-end system tests.

---

### 12.2 Test Infrastructure

**REQ-TEST-INFRA-001:** The system SHOULD support mocking LLM responses for deterministic testing of agent logic.

**REQ-TEST-INFRA-002:** The system SHOULD provide test datasets across multiple domains for validation.

**REQ-TEST-INFRA-003:** The test suite MUST complete in <30 minutes for rapid development feedback.

---

### 12.3 Continuous Integration

**REQ-TEST-CI-001:** The system SHOULD run all automated tests on every code commit.

**REQ-TEST-CI-002:** The system MUST NOT be deployed to production if any MUST/SHALL requirements fail their tests.

**REQ-TEST-CI-003:** The system SHOULD track test coverage metrics over time and prevent coverage regression.

---

## 13. Documentation Requirements

**REQ-DOC-001:** The system MUST provide user documentation explaining how to configure and run research workflows.

**REQ-DOC-002:** The system MUST provide developer documentation explaining system architecture and component interactions.

**REQ-DOC-003:** All configuration parameters MUST be documented with types, valid ranges, and default values.

**REQ-DOC-004:** All requirements in this specification MUST have traceable links to implementing code and validating tests.

**REQ-DOC-005:** The system SHOULD provide example workflows demonstrating capabilities across different domains.

---

## 14. System Limitations and Constraints

This section documents known limitations explicitly acknowledged in the research paper to set realistic expectations for system capabilities.

**REQ-LIMIT-001:** 🚫 The system MUST NOT support mid-cycle human interaction - research workflows execute autonomously once initiated.

**REQ-LIMIT-002:** 🚫 The system MUST NOT autonomously access external public databases or APIs without explicit configuration by the user.

**REQ-LIMIT-003:** The system SHALL warn users that research outcomes are sensitive to the phrasing of research objectives and that rephrasing may yield different results.

**REQ-LIMIT-004:** The system SHALL warn users that it may generate statistically sound but conceptually "unorthodox" metrics that require human interpretation and validation.

**REQ-LIMIT-005:** 🚫 The system MUST NOT conflate statistical significance with scientific importance - all findings MUST be marked as requiring human validation for scientific value assessment.

---

## Requirements Summary

### Total Requirements: 293

**By Priority Level:**
- MUST/SHALL (Critical): 234 requirements (79.9%)
- SHOULD (Recommended): 53 requirements (18.1%)
- MAY (Optional): 6 requirements (2.0%)

**By Requirement Type:**
- Positive Requirements (MUST DO): 237 requirements (80.9%)
- Negative Requirements (MUST NOT): 56 requirements (19.1%)

**By Category:**
- Core Infrastructure: 35 requirements (11.9%)
- Data Analysis Agent: 48 requirements (16.4%)
- Literature Search Agent: 13 requirements (4.4%)
- Structured World Model: 27 requirements (9.2%)
- Orchestrator: 37 requirements (12.6%)
- Integration and Coordination: 12 requirements (4.1%)
- Output and Traceability: 22 requirements (7.5%)
- Domain and Data: 17 requirements (5.8%)
- Performance and Scalability: 21 requirements (7.2%)
- Scientific Validity: 29 requirements (9.9%)
- Security and Safety: 15 requirements (5.1%)
- Testing and Validation: 9 requirements (3.1%)
- Documentation: 5 requirements (1.7%)
- System Limitations: 5 requirements (1.7%)
- Meta-Requirements: 3 requirements (1.0%)

---

## Requirement Priorities by Development Phase

### Phase 1: Infrastructure Validation (COMPLETE)
Requirements validated in initial testing phase focusing on core component functionality.

### Phase 2: Core Research Loop (CURRENT)
Critical requirements for autonomous multi-iteration research capability:
- REQ-ORCH-ITER-001, REQ-ORCH-ITER-002 (Multi-iteration cycles)
- REQ-ORCH-TASK-001, REQ-ORCH-TASK-002 (Task planning)
- REQ-DOMAIN-001 (Multi-domain support)
- REQ-DAA-CAP-001 through REQ-DAA-CAP-004 (Basic analysis)
- REQ-WM-QUERY-001 (Context retrieval)

### Phase 3: Integration Hardening
Requirements for robust component integration and advanced features:
- REQ-INT-PAR-001 through REQ-INT-PAR-004 (Parallel execution)
- REQ-ORCH-ERR-003, REQ-ORCH-ERR-004 (Error recovery)
- REQ-DAA-CAP-005, REQ-DAA-CAP-006 (Advanced analysis)
- REQ-PERF-STAB-001, REQ-PERF-STAB-002 (Long-run stability)

### Phase 4: Production Readiness
Requirements for deployment and operational excellence:
- REQ-OUT-PROV-001 through REQ-OUT-PROV-005 (Provenance)
- REQ-OUT-RPT-001 through REQ-OUT-RPT-005 (Report generation)
- REQ-SEC-* (All security requirements)
- REQ-TEST-CI-* (CI/CD requirements)
- REQ-PERF-STAB-003, REQ-PERF-STAB-004 (Scale testing)

---

## Compliance and Traceability

### Requirement Traceability
Each requirement SHALL be traced to:
1. **Implementing Code:** File and function/class that implements the requirement
2. **Validating Test(s):** Test(s) that verify compliance
3. **Documentation:** User or developer docs explaining the capability

### Compliance Reporting
The testing framework SHALL generate compliance reports indicating:
- Requirements validated (PASS)
- Requirements not yet implemented (NOT IMPLEMENTED)
- Requirements failing validation (FAIL)
- Test coverage percentage for MUST/SHALL requirements

### Production Readiness Criteria
The system SHALL be considered production-ready when:
1. All MUST/SHALL requirements PASS their validating tests
2. >90% of SHOULD requirements PASS their validating tests
3. Test coverage >80% for core functionality
4. All security requirements (REQ-SEC-*) validated
5. Documentation complete (REQ-DOC-*)

---

## Appendix A: Negative Requirements Index

This appendix provides a quick reference to all negative requirements (MUST NOT / SHALL NOT) for security reviews, code reviews, and deployment checklists.

### Critical Safety Requirements (Code Execution)

**REQ-DAA-GEN-005:** 🚫 No hard-coded credentials, absolute paths, or non-portable system calls in generated code
**REQ-DAA-GEN-006:** 🚫 No `eval()` or `exec()` on untrusted input
**REQ-DAA-GEN-007:** 🚫 No modification of global state or environment variables
**REQ-DAA-EXEC-009:** 🚫 No arbitrary shell commands; subprocess spawning restricted to allowlisted scientific tools
**REQ-DAA-EXEC-010:** 🚫 No modification of system environment variables
**REQ-DAA-EXEC-011:** 🚫 No execution if sandbox initialization fails
**REQ-DAA-SAFE-004:** 🚫 No execution of code importing unauthorized modules (os.system, subprocess, socket)
**REQ-DAA-SAFE-006:** 🚫 No file access outside designated data and output directories
**REQ-DAA-SAFE-007:** 🚫 No infinite loops or unbounded recursion

### Security & Data Protection

**REQ-LLM-008:** 🚫 No exposure of LLM API keys in logs or outputs
**REQ-LLM-009:** 🚫 No sending raw sensitive data to LLMs without sanitization
**REQ-LLM-010:** 🚫 No using LLM responses as ground truth without validation
**REQ-LLM-011:** 🚫 No infinite LLM retry loops
**REQ-LLM-012:** 🚫 No exposure of internal prompts in user outputs
**REQ-SEC-EXEC-001:** 🚫 No host file system access (except designated directories)
**REQ-SEC-EXEC-002:** 🚫 No network access from generated code
**REQ-SEC-EXEC-003:** 🚫 No arbitrary system command execution
**REQ-SEC-DATA-001:** 🚫 No sensitive data in logs or outputs
**REQ-SEC-API-004:** 🚫 No sending user data to external APIs without consent
**REQ-SEC-API-005:** 🚫 No caching sensitive API responses in plaintext

### Scientific Validity & Integrity

**REQ-LSA-010:** 🚫 No citing retracted papers
**REQ-LSA-011:** 🚫 No relying solely on non-peer-reviewed sources for primary evidence
**REQ-LSA-012:** 🚫 No synthesizing contradictory findings without noting conflicts
**REQ-SCI-HYP-005:** 🚫 No hypotheses contradicting established physical laws without justification
**REQ-SCI-HYP-006:** 🚫 No claiming causation from correlation without proper design
**REQ-SCI-ANA-005:** 🚫 No statistical tests on data grossly violating assumptions
**REQ-SCI-ANA-006:** 🚫 Report effect sizes with p-values; confidence intervals SHOULD be included when applicable
**REQ-SCI-ANA-007:** 🚫 No cherry-picking or selective reporting of analyses
**REQ-SCI-REPRO-005:** 🚫 No guaranteeing deterministic results - discovery process is inherently stochastic

### System Limitations & Constraints

**REQ-LIMIT-001:** 🚫 No mid-cycle human interaction support
**REQ-LIMIT-002:** 🚫 No autonomous external database access without explicit configuration
**REQ-LIMIT-005:** 🚫 No conflating statistical significance with scientific importance without human validation

### Data Integrity

**REQ-DATA-006:** 🚫 No modification of original input datasets
**REQ-DATA-007:** 🚫 No proceeding with critical data quality issues (>50% missing, schema mismatches)
**REQ-DATA-008:** 🚫 No mixing data from different domains without explicit instruction
**REQ-DATA-009:** 🚫 No accepting datasets without provenance information
**REQ-DATA-010:** 🚫 No claiming support for datasets >5GB (known limitation)
**REQ-DATA-012:** 🚫 No processing raw image data or raw sequencing files
**REQ-DOMAIN-002:** 🚫 No domain-specific code modifications required

### World Model Integrity

**REQ-WM-CRUD-006:** 🚫 No deleting entities with active references without resolution
**REQ-WM-CRUD-007:** 🚫 No updates breaking referential integrity
**REQ-WM-PERSIST-005:** 🚫 No retroactive modification of provenance records
**REQ-WM-PERSIST-006:** 🚫 No merging conflicting information without resolution

### Orchestrator Safety

**REQ-ORCH-ITER-006:** 🚫 No infinite iteration loops - hard limit enforced
**REQ-ORCH-ITER-007:** 🚫 No proceeding with inconsistent World Model state
**REQ-ORCH-ERR-005:** 🚫 No retrying tasks that fail safety validation
**REQ-ORCH-ERR-006:** 🚫 No ignoring critical errors
**REQ-ORCH-ERR-007:** 🚫 No executing contradictory tasks simultaneously
**REQ-INT-PAR-002:** 🚫 No data corruption from parallel execution

### Configuration & Deployment

**REQ-CFG-005:** 🚫 No execution with invalid/missing critical configuration
**REQ-TEST-CI-002:** 🚫 No production deployment if critical tests fail

### Performance Boundaries

**REQ-PERF-RES-004:** 🚫 No blocking workflow on slow APIs without timeouts
**REQ-PERF-RES-005:** 🚫 No loading entire large datasets (>1GB) into memory if streaming possible
**REQ-PERF-RES-006:** 🚫 No exponential complexity algorithms on large datasets (n>1000) without confirmation

---

### Using This Index

**For Code Reviews:**
1. Check all code changes against relevant negative requirements
2. Verify AST-based static analysis catches prohibited operations
3. Ensure test coverage for negative requirements

**For Security Audits:**
1. Validate all 🚫 requirements in Security & Data Protection section
2. Test sandbox isolation (REQ-DAA-EXEC-*, REQ-SEC-EXEC-*)
3. Verify no sensitive data leakage (REQ-SEC-DATA-*, REQ-LLM-008/009)

**For Deployment:**
1. Confirm all configuration negative requirements (REQ-CFG-005)
2. Validate all tests pass (REQ-TEST-CI-002)
3. Review data handling requirements (REQ-DATA-006 through REQ-DATA-009)

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 Draft | 2025-11-20 | Initial | Complete requirements specification for review |
| 1.1 Draft | 2025-11-20 | Updated | Added 41 negative requirements (MUST NOT) across all categories; Added Appendix A: Negative Requirements Index; Updated statistics (203→244 total requirements) |
| 1.2 Draft | 2025-11-20 | Updated | Added 22 paper-specific requirements based on detailed Kosmos paper analysis: performance benchmarks (3), accuracy targets by statement type (4), dataset size limitations (3), stochastic behavior documentation (3), known system limitations (5), world model specifics (3), convergence override (1); Added Section 14: System Limitations and Constraints; Updated Appendix A with 6 new negative requirements; Updated statistics (244→266 total requirements) |
| 1.3 Draft | 2025-11-20 | Updated | Added 5 critical requirements from second external validation: self-correction loop for autonomous code debugging (REQ-DAA-EXEC-012), literature processing throughput (REQ-LSA-013), metabolomics libraries (REQ-ENV-006), materials science libraries (REQ-ENV-007), explicit parallel task limit (REQ-ORCH-TASK-007); Elevated 2 requirements from SHOULD to MUST: genetics libraries (REQ-ENV-004) and prompt caching (REQ-LLM-007) for economic viability; Updated statistics (266→271 total requirements) |
| 1.4 Draft | 2025-11-20 | Updated | **Major update from three external AI validations:** Removed 1 contradictory requirement (REQ-SCI-VAL-003 - impossible 100% accuracy); Added 23 new requirements: seven-phase discovery cycle (REQ-ORCH-CYCLE-001), hypothesis generation mechanism (REQ-ORCH-SYN-001), analytical pivoting on failure (REQ-ORCH-ERR-008), multi-report generation (REQ-OUT-RPT-006-009), discovery narrative identification (REQ-OUT-DISC-001), statement type classification (REQ-OUT-CLASS-001-002), specific scale targets (REQ-PERF-SCALE-001-003: 40K lines code, 1K papers, 150+ rollouts), accuracy benchmarks by statement type (REQ-SCI-VAL-004-007), expert time metrics (REQ-SCI-METRIC-001-002), novelty/depth assessment (REQ-SCI-EVAL-001-002), pathway analysis (REQ-DAA-CAP-008), novel analytical methods (REQ-DAA-CAP-009); Upgraded 6 requirements from SHOULD to MUST (parallel execution, convergence detection, advanced analysis, visualization, Jupyter notebooks, full-text retrieval); Downgraded 3 from MUST to SHOULD (uptime SLA, regulatory compliance, pause/resume) to align with research prototype scope; Modified 4 requirement texts for paper accuracy; Updated statistics (271→293 total requirements) |

---

## Next Steps

1. **Requirements Review:** Stakeholder review and refinement of requirements
2. **Prioritization:** Finalize phase assignments for each requirement
3. **Acceptance Criteria:** Define measurable acceptance criteria for subjective requirements
4. **Test Planning:** Create test specifications mapping requirements to test cases
5. **Traceability Matrix:** Build requirement → code → test mapping
6. **Implementation:** Begin systematic validation of requirements by phase

---

**Document Status:** Draft - Pending Review
**Approval Required:** Yes
**Review Deadline:** TBD

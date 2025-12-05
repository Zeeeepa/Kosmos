# E2E Testing Resume Prompt 13

## Quick Context

Copy and paste this into a new Claude Code session to continue:

---

```
@VALIDATION_ROADMAP.md
@E2E_CHECKPOINT_20251128_SESSION12.md

Continue from Session 12. Bug fixes done, but 5-cycle workflow blocked by context limit.

## Current State
- E2E tests: 38 passed, 0 failed, 1 skipped
- Bug fixes applied: max_results duplicate, NoneType validation
- Phase 3.2: Blocked by Ollama 8k context limit

## Key Finding (Session 12)
The Ollama model (qwen3-kosmos-fast) has only 8k token context.
- Experiment designer prompts exceed this limit (300s timeout)
- Hypothesis generator sometimes fails JSON parse (context overflow)
- Need larger context model (DeepSeek with 64k+)

## Recommended Session 13 Focus

Option A: Switch to DeepSeek
- Configure DeepSeek API
- Retry 5-cycle workflow
- Should complete without timeouts

Option B: Optimize Prompts
- Reduce experiment designer prompt size
- Simplify system prompts
- May allow Ollama to work

## Files Modified in Session 12
- kosmos/literature/unified_search.py (max_results fix)
- kosmos/agents/experiment_designer.py (NoneType fix)

## DeepSeek Configuration (if available)
```bash
export LLM_PROVIDER=litellm
export LITELLM_MODEL=deepseek/deepseek-chat
export LITELLM_API_BASE=https://api.deepseek.com
export DEEPSEEK_API_KEY=your_key_here
```
```

---

## Session History

| Session | Focus | Results | Phase |
|---------|-------|---------|-------|
| 11 | Phase 3.1 | Baseline | 3 cycles, 8.2 min |
| 12 | Phase 3.2 | Bug fixes | Context limit blocked |
| 13 | TBD | TBD | Retry with DeepSeek |

---

## Known Issues

1. **Context Limit (BLOCKING)**
   - Ollama 8k context too small for experiment designer
   - Solution: Use DeepSeek or other large-context model

2. **Semantic Scholar Date Bug (non-blocking)**
   - `strptime()` error on already-datetime values
   - File: `kosmos/literature/semantic_scholar.py:335`

---

*Resume prompt created: 2025-11-28*

# Memory-Augmented TAP — Bachelor's Project Roadmap

**Project:** Adding a retrieval-based learning loop to the TAP jailbreak framework, so the
attacker improves its attack success rate over time without fine-tuning any model.

**Working title:** *Memory-Augmented TAP: A Retrieval-Based Learning Framework for Iterative
Jailbreak Attack Generation*

**Core research question:** Does seeding TAP's attacker with a growing memory of past
successful attacks increase attack success rate (ASR) and/or reduce queries-to-success across
iterations, compared to stateless TAP?

> Keep this file as your single source of truth. Tick things off as you go.

---

## 0. The One-Paragraph Summary (memorize this)

Standard TAP is **stateless** — every run starts cold and reinvents the wheel. You will make it
**stateful** by attaching a memory bank (a vector database) of past attacks. Before each run, the
attacker retrieves the most relevant high-scoring past attacks and uses them as few-shot
examples. After each run, new successful attacks are stored back. "Learning" is defined
**behaviorally**: ASR rises monotonically across iterations against a fixed target, with **no
model weights changed**. That last clause is what keeps the project feasible on a student budget.

---

## 1. Reading List

You've read **TAP** and **GCG**. Good, but you're missing the single most important paper for
your project.

### MUST READ (in this order)

| # | Paper | Why it matters to you |
|---|---|---|
| 1 | **PAIR** — *Jailbreaking Black Box LLMs in Twenty Queries* (Chao et al., 2023, arXiv 2310.08419) | This is the **direct predecessor of TAP**. TAP is literally "PAIR + tree search with pruning." It's simpler than TAP and will make TAP click fully. Read this BEFORE writing any code. |
| 2 | **RAG original** — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (Lewis et al., 2020, arXiv 2005.11401) | The paper that named RAG. **Skim it** for the concept (retrieve-then-generate). Note: modern RAG is much simpler than this paper's architecture — don't get bogged down. |
| 3 | **JailbreakBench** (Chao et al., NeurIPS 2024, arXiv 2404.01318 / jailbreakbench.github.io) | Your **evaluation backbone**. Provides the JBB-Behaviors dataset (100 harmful behaviors in 10 categories), a standardized judge, and released PAIR/GCG attack artifacts. Using it makes your numbers credible and comparable. |

### SHOULD READ (skim, for context + related-work section)

| Paper | Why |
|---|---|
| **HarmBench** (Mazeika et al., 2024, arXiv 2402.04249) | The other standard eval framework. Cite it; you don't have to use it. |
| **AutoDAN** (Liu et al., 2023) | Genetic-algorithm jailbreaks. Useful if you ever want to frame your memory as an "evolutionary" mechanism, and good for related work. |
| One **survey** on LLM jailbreaks (e.g. arXiv 2403.04786, "Breaking Down the Defenses") | Gives you a clean taxonomy (white-box vs black-box, gradient vs semantic) for your intro chapter. |

### DON'T over-read
You do NOT need to deep-dive the RAG/transformer internals or read 20 jailbreak papers. Your
contribution is the **memory loop**, not a new attack primitive. Budget ~1 week for reading, then
start building.

---

## 2. Learning RAG From Zero

You said you know nothing about RAG. The good news: **RAG is a pattern, not a hard algorithm.**
It's "search a database, then paste the results into the prompt." That's it.

### The 4 concepts you must understand
1. **Embeddings** — a model turns text into a vector (list of numbers) that captures meaning.
   Similar meaning → vectors close together.
2. **Vector database** — stores those vectors and lets you search by similarity.
3. **Similarity search** — given a query vector, find the top-k closest stored vectors (cosine similarity).
4. **Context injection** — take the retrieved text and format it into the prompt. Just string formatting.

### Hands-on learning path (do these in order — about 2–3 days total)

- [x] **Step A — Feel embeddings.** Install `sentence-transformers`. Encode 5 sentences, print the
  vectors, compute cosine similarity between pairs by hand. Confirm that similar sentences score higher.
- [ ] **Step B — ChromaDB quickstart.** Do the official ChromaDB getting-started. Store 10 short
  texts, query 3 back. ~20 minutes.
- [ ] **Step C — Mini end-to-end RAG.** Store 10 facts, take a question, retrieve top-3, paste them
  into a prompt to an LLM, get an answer. This is the whole RAG pattern in ~40 lines.
- [ ] **Step D — Read one good RAG explainer blog** (search "RAG from scratch" — pick a recent one
  with code). Skip anything selling a framework; you want the raw pattern.

### Tools (don't overthink the stack)
- **Embeddings:** `sentence-transformers` (model: `all-MiniLM-L6-v2` is small + fine to start).
- **Vector DB:** **ChromaDB** (easiest) or **FAISS** (faster, no server). Start with Chroma.
- **Avoid** heavy frameworks (LangChain/LlamaIndex) for the core — they hide the mechanism you're
  supposed to understand and demonstrate. You can mention them in "tools considered."

---

## 3. Implementation Phases

### Phase 1 — Reproduce the TAP baseline (≈ 3–4 weeks)
- [ ] Get the official TAP repo running against a target model you can afford to query a lot
      (a local open-weights model like a small Llama/Vicuna/Mistral via Ollama is ideal — free, fast, no API bill).
- [ ] Use the **JailbreakBench JBB-Behaviors** dataset as your set of attack goals.
- [ ] Reproduce baseline metrics: **ASR** and **average queries-to-success** on a fixed subset
      (e.g. 50 behaviors). Lock these numbers — they are your control group.
- [ ] **Deliverable:** a working, instrumented TAP that logs every `(goal, prompt, target_response, score)` tuple.

> The logging is critical — those tuples ARE the data your memory bank will be built from.
  
### Phase 2 — Build the memory layer (≈ 4–5 weeks)
- [ ] Build the store: a Chroma collection holding `(prompt, embedding, score, goal_category, strategy_tag)`.
- [ ] **Write path:** after each run, store successful prompts (score above threshold) back into the DB.
- [ ] **Read path:** at the start of each run, embed the goal, retrieve top-k past attacks, inject
      them as few-shot examples into the attacker's system prompt.
- [ ] Implement the **three learning mechanisms** (add them incrementally so each is its own ablation):
  1. **Plain retrieval** — top-k by semantic similarity only.
  2. **Score-weighted retrieval** — rank by `similarity × score` so winners get surfaced more.
  3. **Strategy tagging** *(if time allows)* — after a success, ask an LLM to label the strategy
     in 2–3 words (e.g. `roleplay_authority`, `fictional_framing`), store the tag, and let
     retrieval reason at the strategy level. This is your most novel piece.

### Phase 3 — Evaluate & compare (≈ 3–4 weeks)
- [ ] Run the full experiment (see Section 4) and produce the curves + ablation table.
- [ ] Sanity checks: fixed random seeds, same target model, same judge, same behavior set across
      all conditions. Only the memory mechanism changes.

### Phase 4 — Write-up + optional paper (≈ 3–4 weeks)
- [ ] Thesis chapters: Intro → Background (TAP/PAIR/RAG) → Method → Experiments → Results → Discussion → Future Work.
- [ ] Clean the GitHub repo (README, reproduce instructions, requirements.txt). The repo itself is
      a CV asset for grad applications.
- [ ] *(Optional stretch)* condense into a 4–8 page workshop paper.

---

## 4. How You Prove "Learning" Happened (Evaluation Design)

This section is the scientific heart of the project. Three metrics:

1. **ASR over iterations** — x-axis = run number, y-axis = % of goals where a jailbreak above
   threshold was found. **Rising curve = learning.** This is your headline result.
2. **Queries / nodes to success** — does the system find a successful attack *faster* (fewer tree
   nodes explored) as the memory grows? A falling curve = the memory provides useful signal.
3. **Ablation table** — the comparison that makes it rigorous:

   | Condition | ASR | Avg queries-to-success |
   |---|---|---|
   | Stateless TAP (baseline) | … | … |
   | TAP + plain retrieval | … | … |
   | TAP + score-weighted retrieval | … | … |
   | TAP + strategy tags | … | … |

**Define "learning" explicitly in the thesis:** *monotonic improvement in ASR across iterations
against a fixed target model, with no change to model weights.* Clean, defensible, comparable to
prior work.

### Optional ML extension (only if you have time / want a classic-ML component)
Train a tiny **surrogate success classifier** (logistic regression or small BERT on prompt
embeddings → success/fail) on your growing DB. Use it to pre-rank candidate prompts and only send
the top few to the expensive LLM judge → saves queries. Trainable on a laptop. Great "future work"
or extension chapter; shows research maturity without LLM fine-tuning pain.

---

## 5. Why NOT to Fine-Tune (keep this decision documented)

You will be tempted, and a reviewer may ask. Reasons to keep learning at the **system level**:
- Fine-tuning needs real GPU compute (cost) and weeks of pipeline plumbing.
- A changed-weights "black box" can't tell you *why* attacks improved — bad for a thesis narrative.
- Retrieval-based learning is **interpretable and ablatable** — you can point at exactly which
  retrieved examples drove an improvement.
- It keeps the project finishable solo in one semester.

If a committee wants a "real ML" angle, the **surrogate classifier** (Section 4) gives you trainable
ML on a laptop — without touching the attacker's weights.

---

## 6. Suggested Timeline (≈ 14–16 weeks)

| Weeks | Focus |
|---|---|
| 1 | Read PAIR + skim RAG paper + JailbreakBench. Do the RAG hands-on path (Section 2). |
| 2–5 | Phase 1: reproduce TAP baseline, set up logging + local target model. |
| 6–10 | Phase 2: build memory bank + the three retrieval mechanisms. |
| 11–13 | Phase 3: run experiments, produce curves + ablation. |
| 14–16 | Phase 4: write thesis, clean repo, (optional) draft workshop paper. |

---

## 7. Risks & Practical Tips

- **API cost trap:** querying GPT-4 thousands of times is expensive. Use a **local open-weights
  model** (Ollama + a small Llama/Mistral) as your target so experiments are free and fast. Mention
  in limitations that closed-model results are future work.
- **Cold-start:** an empty DB gives no benefit on run 1. That's expected and is part of the story —
  the *curve* is the contribution, not run-1 performance.
- **Judge consistency:** use the JailbreakBench standardized judge so "success" means the same
  thing across all conditions. Don't hand-tune the judge per experiment.
- **Reproducibility:** fix seeds, log everything, commit configs. Grad committees notice clean
  experimental hygiene.
- **Ethics framing (do this on day 1):** frame the project as **defensive security / red-teaming
  research** — understanding attacks to build better defenses, the standard framing in this
  literature (HarmBench and JailbreakBench both release attacks for exactly this reason). Confirm
  your department is fine with it early, and don't release working attacks against production models.

---

## 8. Quick Reference — The Modified TAP Loop

```
New attack goal arrives
      │
      ▼
Embed goal ──► query vector DB ──► retrieve top-k high-scoring past attacks
      │                                   (similarity × score)
      ▼
Inject retrieved attacks as few-shot examples into Attacker's system prompt
      │
      ▼
Run TAP as normal (attacker generates ► evaluator scores ► prune tree)
      │
      ▼
Store new successful prompts (+ strategy tag) back into the DB   ◄── this is the "learning"
```

The DB grows → seeds get better → ASR rises across runs. That rising curve is your thesis.

---

## 9. Citations to keep handy

- Mehrotra et al., 2023 — *Tree of Attacks (TAP)* — arXiv 2312.02119
- Chao et al., 2023 — *PAIR* — arXiv 2310.08419
- Zou et al., 2023 — *GCG* — arXiv 2307.15043
- Lewis et al., 2020 — *RAG* — arXiv 2005.11401
- Chao et al., 2024 — *JailbreakBench* (NeurIPS 2024) — arXiv 2404.01318
- Mazeika et al., 2024 — *HarmBench* — arXiv 2402.04249
- Liu et al., 2023 — *AutoDAN* — arXiv 2310.04451

*(Double-check each arXiv ID when you cite — pull the exact bibtex from the arXiv page.)*
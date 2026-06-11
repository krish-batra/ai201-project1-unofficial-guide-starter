# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

     This system makes student reviews of CS professors at the University of Pittsburgh searchable and answerable. Students rely heavily on peer opinions when choosing courses and professors, but this knowledge is scattered across Rate My Professors, Reddit threads, and word-of-mouth. No official channel — not the course catalog, department website, or syllabus — tells you whether a professor curves exams, how strict their AI policy is, how responsive they are outside class, or whether their projects are manageable. This system surfaces that real, student-generated knowledge in response to plain-language questions.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->


| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Rate My Professors|Reviews of Jarrett Billingsley (CS0447, CS0449)|https://www.ratemyprofessors.com/professor/2354970|
| 2 |Rate My Professors|Reviews of Luis Oliveira (CS0447, CS0449)|https://www.ratemyprofessors.com/professor/2447491|
| 3 |Rate My Professors|Reviews of John Ramirez (CS0401, CS0445)|https://www.ratemyprofessors.com/professor/9338|
| 4 |Rate My Professors|Reviews of William Garrison (CS0441, CS1501, CMPINF0010)|https://www.ratemyprofessors.com/professor/2055608|
| 5 |Rate My Professors|Reviews of Sherif Khattab (CS1501, CS1550, CS0445)|https://www.ratemyprofessors.com/professor/2313893|
| 6 |Rate My Professors|Reviews of Nick Farnan (CS1501, CS1520, CS0441)|https://www.ratemyprofessors.com/professor/1894664|
| 7 |Rate My Professors|Reviews of Patricia Quirin (CS0590)|https://www.ratemyprofessors.com/professor/613274|
| 8 |Rate My Professors|Reviews of Daniel Mahoney (CS1660)|https://www.ratemyprofessors.com/professor/2926337|
| 9 |Rate My Professors|Reviews of Patrick Skeba (CS1503, CS1675, CMPINF0010)|https://www.ratemyprofessors.com/professor/2937623|
| 10|Rate My Professors|Reviews of Sohel Sarwar (CS1530)|https://www.ratemyprofessors.com/professor/2450152|

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 Characters

**Overlap:** 100 Characters

**Why these choices fit your documents:** Each document is a collection of short student reviews ranging from 1 to roughly 10 sentences. A chunk size of 500 characters captures one complete review or a meaningful portion of a longer one without merging multiple unrelated reviews together. Merging reviews would dilute semantic signal — a chunk mixing opinions about exam difficulty and professor personality would match weakly against any specific query. A 100-character overlap ensures that key facts near chunk boundaries (like "exams are curved" or "don't use AI") appear fully in at least one chunk rather than being split across two. Character-based splitting was chosen over paragraph splitting because the documents use dash separators rather than blank lines between reviews, making paragraph detection unreliable.
Before chunking, documents were cleaned by removing repeated dash separators and collapsing excess blank lines. The header block at the top of each file (professor name, department, URL, overall rating) was kept because it provides context that helps with professor-name matching during retrieval.

**Final chunk count:** 292 chunks across 10 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers. 
This model runs locally with no API key and no rate limits, producing 384-dimensional embeddings. It is well-suited to short informal text like student reviews and has no per-query cost, which makes it practical for a project of this scale.

**Production tradeoff reflection:** For a production deployment I would weigh several factors. On accuracy, all-MiniLM-L6-v2 is a general-purpose model; a model fine-tuned on opinion or review text such as all-mpnet-base-v2 or OpenAI's text-embedding-3-small might capture informal student language and subject-specific vocabulary more precisely. On context length, all-MiniLM-L6-v2 supports 256 tokens, which is sufficient for 500-character chunks, but a longer-context model would be necessary for larger documents like syllabi or course guides. On cost, local models are free while API-based embeddings from OpenAI or Cohere cost per token — negligible at this scale but significant at millions of queries. On latency, local inference has no network round-trip, making it faster for real-time use. On multilingual support, if the system were expanded to serve international students writing reviews in other languages, a multilingual model like paraphrase-multilingual-MiniLM-L12-v2 would be required since all-MiniLM-L6-v2 is English-only.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The following system prompt is passed to the Groq LLM (llama-3.3-70b-versatile) on every query:
You are a helpful assistant that answers questions about CS professors at the
University of Pittsburgh.

IMPORTANT RULES:
1. Answer ONLY using the information provided in the documents below.
2. Do NOT use any outside knowledge or make assumptions beyond what the
   documents say.
3. Always cite which document(s) your answer comes from at the end of your
   response, under a "Sources:" heading.
4. If the provided documents do not contain enough information to answer the
   question, say exactly: "I don't have enough information in my documents to
   answer that question."
5. Be concise and direct. Quote specific student reviews when they support
   your answer.

   The retrieved chunks are injected into the user message as labeled document blocks (e.g., "[Document 1 — Source: rmp_jarrett_billingsley.txt]") so the model can reference them by number. Temperature is set to 0.2 to reduce creative generation and keep responses closer to the retrieved text.

**How source attribution is surfaced in the response:** Source attribution is enforced in two ways. First, the system prompt instructs the LLM to include a "Sources:" section naming which documents it used. Second, the generate_answer() function in generate.py programmatically collects the source filenames from the retrieved chunks and appends them to the response as a "Retrieved from" list — so attribution is guaranteed even if the LLM omits it from its own response.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Does Jarrett Billingsley allow AI on assignments?|No — strict no-AI policy, students were failed for using it | "No, Jarrett Billingsley does not allow AI... failed around 60% of the class for using AI" with quotes from reviews| Relevant| Accurate|
| 2 |Are Nick Farnan's exams open book? |Yes — take-home and open note | "Nick Farnan's exams are open note... Exams are open note and weren't too bad if you study his lecture notes"| Relevant| Accurate|
| 3 | How difficult are Luis Oliveira's midterms?|Very difficult — class average around 55–60% | "midterms are considered difficult... average for the midterm was a 57... Exams felt like brand new information"| Partilly Relevant | Accurate|
| 4 | Does John Ramirez use a flipped classroom format?| Yes — pre-recorded videos before class, TopHat in class|"Yes, John Ramirez uses a flipped classroom format where students watch pre-recorded lecture videos before class" | Relevant| Accurate|
| 5 | Is Patricia Quirin's CS0590 class easy to get an A in?|Yes — very lenient, extensions allowed, essay resubmissions | "CS0590 with Patricia Quirin is considered an easy class... very lenient with extensions and allows essay resubmissions"|Relevant | Accurate|

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "How difficult are Luis Oliveira's midterms?" (Question 3)

**What the system returned:** The system returned relevant chunks and produced an accurate answer, but the retrieval distance scores were noticeably higher (1.05–1.18) compared to questions 1 and 2 (0.75–0.93). This made it the weakest retrieval of the five evaluation queries.

**Root cause (tied to a specific pipeline stage):** The failure is at the retrieval stage and is caused by a vocabulary mismatch between the query and the documents. The query uses the word "midterms" but most student reviews use "exams" or "tests" instead. The all-MiniLM-L6-v2 embedding model maps these as semantically similar but not identical, which increases the distance score. The relevant information exists in the documents but ranks lower than it would if the vocabulary matched exactly. This is a known limitation of dense retrieval: it handles semantic similarity well but can underrank results when the query uses a specific term (like "midterm") that reviewers tend to express differently (like "exam" or "test").

**What you would change to fix it:** Adding a hybrid search approach (BM25 keyword search combined with semantic search) would help here. BM25 would boost results that contain the exact word "midterm" regardless of embedding distance, and combining it with semantic scores would produce more robust rankings. Alternatively, query expansion, automatically adding synonyms like "exams" and "tests" to the query before embedding would also improve recall for this type of vocabulary mismatch.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**  Writing the evaluation plan in planning.md before any code forced me to pick 5 specific, verifiable questions with real expected answers drawn from the documents I had already collected. This made Milestone 6 straightforward — I already knew exactly what to test and what "correct" looked like before I ran a single query. Without the spec, I might have tested vague questions like "tell me about Billingsley" and accepted whatever the system returned as good enough. The specific questions also revealed the vocabulary mismatch failure case in Question 3, which I would not have noticed with a looser evaluation standard.

**One way your implementation diverged from the spec, and why:**  The planning.md anticipated that retrieval distance scores would be below 0.5, based on language in the project instructions. In practice, all-MiniLM-L6-v2 with ChromaDB produces distances in the 0.75–1.18 range for this corpus. This is a property of ChromaDB's default distance metric (squared L2) combined with the embedding space of this particular model — it does not mean retrieval is performing poorly. The chunks returned are topically correct and produce accurate answers. I updated my interpretation of "good" distance scores for this model rather than changing the chunking strategy or switching embedding models, because the retrieval results themselves were clearly on-topic when inspected manually.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*  I gave Claude the Chunking Strategy section from planning.md (500-char chunks, 100-char overlap, character-based splitting) and the Documents section (10 .txt files in a documents/ folder). I asked it to implement load_documents() and chunk_text() matching those exact parameters.
- *What it produced:*  Claude produced a complete ingest.py with load_documents(), clean_text(), chunk_text(), a build_chunks() orchestrator, and an inspect_chunks() printer for manual verification.
- *What I changed or overrode:*  I ran python ingest.py and printed 5 sample chunks to verify the output before accepting the code. The chunks were readable and had correct source filenames attached. I confirmed the chunk count (292) was in the acceptable range (100–500) specified in the project instructions. I did not need to override the chunk size or overlap since the output matched the spec, but I verified each function independently rather than trusting the generated code blindly.

**Instance 2**

- *What I gave the AI:*  I gave Claude the Retrieval Approach section of planning.md (model: all-MiniLM-L6-v2, top-k: 5, ChromaDB storage), the Architecture diagram, and the grounding requirement from the project spec ("answer only from retrieved context, cite sources, refuse if documents don't contain the answer").
- *What it produced:*  Claude produced retrieve.py with embed_and_store() and retrieve(), and generate.py with generate_answer() and a Groq system prompt. It also produced app.py with the Gradio interface wiring the two together.
- *What I changed or overrode:*  I reviewed the system prompt carefully and confirmed it included both the grounding rule and the explicit refusal instruction for out-of-scope questions. I tested grounding by running an out-of-scope question ("What is a class that has nothing to do with CS at Pitt?") and confirmed the system returned the refusal response rather than hallucinating. I also set temperature=0.2 in the Groq API call (the generated code used the default) to reduce creative generation and keep responses closer to the retrieved text.

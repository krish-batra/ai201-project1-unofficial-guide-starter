# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

This system makes student reviews of CS professors at the University of Pittsburgh searchable and answerable. Students rely heavily on peer opinions when choosing courses and professors, but this knowledge is scattered across Rate My Professors, Reddit threads, and word-of-mouth. No official channel — not the course catalog, department website, or syllabus — tells you whether a professor curves exams, how strict their AI policy is, how responsive they are outside class, or whether their projects are manageable. This system surfaces that real, student-generated knowledge in response to plain-language questions.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500 Characters

**Overlap:** 100 Characters

**Reasoning:** Each document is a collection of short student reviews. Individual reviews range from 1 sentence to roughly 10 sentences — most are 2–5 sentences long. A chunk size of 500 characters is large enough to capture one complete review (or a meaningful portion of a longer one) without merging multiple unrelated reviews together. Merging reviews would dilute the semantic signal — a chunk that mixes opinions about exam difficulty and professor personality would match weakly against any specific query.
A 100-character overlap ensures that if a key fact (like "exams are curved" or "don't use AI") falls near the boundary between two chunks, it will appear in at least one of them fully. Without overlap, a sentence split across a boundary would be retrievable as a fragment in neither chunk.
Chunking by fixed character count rather than paragraph is appropriate here because the documents don't have consistent paragraph structure — reviews are separated by dashes, not blank lines. A character-based splitter with overlap is more reliable than a paragraph splitter for this format.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 5

**Production tradeoff reflection:** For a production deployment, I would weigh the following tradeoffs when choosing an embedding model:

Accuracy on domain-specific text: all-MiniLM-L6-v2 is a general-purpose model trained on broad web text. For student reviews it performs well, but a model fine-tuned on informal/opinion text (like all-mpnet-base-v2 or OpenAI's text-embedding-3-small) might capture nuanced student language better.
Context length: all-MiniLM-L6-v2 has a 256-token limit, which is sufficient for 500-character chunks. For larger documents, a model with a longer context window (e.g., text-embedding-3-large at 8191 tokens) would be necessary.
Cost: all-MiniLM-L6-v2 runs locally for free. OpenAI or Cohere embedding APIs cost per token — for a small corpus like this, that's negligible, but at scale it adds up.
Latency: Local models have no network latency. For a real-time query interface, API-based models add round-trip time that would need to be acceptable for users.
Multilingual support: If the system were expanded to serve international students, a multilingual model like paraphrase-multilingual-MiniLM-L12-v2 would be necessary.

For this project, all-MiniLM-L6-v2 is the right choice: free, fast, locally run, and well-suited to short informal text.
Top-k of 5 balances giving the LLM enough context to synthesize a grounded answer without overwhelming it with loosely related reviews. If too few chunks are retrieved, relevant information may be missing. If too many are retrieved, the LLM may lose focus or pull in off-topic content.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 |Does Jarrett Billingsley allow AI on assignments? | No — Billingsley has a strict no-AI policy. Students who used AI on labs and projects were failed or received zeros. Multiple reviews warn explicitly not to use AI in his class.|
| 2 | Are Nick Farnan's exams open book?|Yes — Farnan's exams are take-home and open note. Multiple reviews confirm this, though they warn not to underestimate them. |
| 3 | How difficult are Luis Oliveira's midterms?| Very difficult — the class average on Oliveira's midterm was around 55–60%. He offered points back, but several reviews describe the exams as much harder than expected.|
| 4 | Does John Ramirez use a flipped classroom format?| Yes — Ramirez uses a flipped classroom model where students watch pre-recorded lecture videos before class and review material during class. TopHat questions are used in class.|
| 5 | Is Patricia Quirin's CS0590 class easy to get an A in?|Yes — CS0590 with Quirin is considered one of the easiest classes at Pitt. Graded on papers, a group project, and discussion boards. She is very lenient with extensions and allows essay resubmissions. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Reviews split across chunk boundaries may lose key facts. Many reviews contain a critical piece of information (e.g., "failed 60% of the class for using AI") in a single sentence. If that sentence falls at the boundary between two chunks, neither chunk may contain it fully, and retrieval may miss it. The 100-character overlap mitigates this but does not eliminate it. I may need to adjust chunk size or overlap if I notice retrieval missing important single-sentence facts during testing.

2. Mixed-sentiment chunks may confuse retrieval. Some reviews in the same document express opposite opinions — one student praises Billingsley's lectures while another criticizes his AI policy. If these get merged into one chunk, embeddings may average out the sentiment and match weakly against either a positive or a negative query. This could cause the system to return a vague chunk when a specific claim was needed. Keeping chunks small (500 characters) reduces the chance of this happening.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

┌─────────────────────────────────────────────────────────────────┐
│                        PIPELINE OVERVIEW                        │
└─────────────────────────────────────────────────────────────────┘

  [1] Document Ingestion          [2] Chunking
  ──────────────────────          ────────────
  Tool: Python (open/read)   →    Tool: custom chunk_text()
  Input: 10 .txt files            chunk_size: 500 chars
  in documents/ folder            overlap: 100 chars
  Output: list of                 Output: list of
  (text, source_filename)         (chunk_text, source, chunk_index)
         │
         ▼
  [3] Embedding + Vector Store
  ────────────────────────────
  Tool: sentence-transformers
        (all-MiniLM-L6-v2)
  + ChromaDB (local)
  Each chunk → 384-dim vector
  Stored with metadata:
    - source filename
    - chunk index
         │
         ▼
  [4] Retrieval                   [5] Generation
  ─────────────                   ──────────────
  Tool: ChromaDB                  Tool: Groq API
  query → embed →            →    (llama-3.3-70b-versatile)
  top-k=5 similar chunks          System prompt enforces
  returned with source            grounding: answer only
  metadata                        from retrieved context
                                  Response includes
                                  source attribution
         │
         ▼
  [6] Query Interface
  ───────────────────
  Tool: Gradio (gradio>=6.9.0)
  Input: text question
  Output: answer + sources list
  Runs at http://localhost:7860
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:** I will give Claude the Documents section (listing the 10 .txt files in documents/) and the Chunking Strategy section (500-char chunks, 100-char overlap, character-based splitting). I will ask Claude to implement two functions: load_documents(folder_path) that reads all .txt files and returns a list of (text, filename) tuples, and chunk_text(text, source, chunk_size=500, overlap=100) that returns a list of dicts with keys text, source, and chunk_index. I will verify the output by printing 5 random chunks and checking that each is under 500 characters, contains readable review text, and has the correct source filename attached.

**Milestone 4 — Embedding and retrieval:** I will give Claude the Retrieval Approach section (model: all-MiniLM-L6-v2, top-k: 5) and the Architecture diagram. I will ask Claude to implement an embed_and_store(chunks) function that embeds all chunks using SentenceTransformer and stores them in a ChromaDB collection with source and chunk_index metadata, and a retrieve(query, k=5) function that embeds the query and returns the top-k chunks with their source filenames and distance scores. I will verify by running 3 of my 5 evaluation questions and checking that the returned chunks are visibly relevant to each question and have distance scores below 0.5.

**Milestone 5 — Generation and interface:** I will give Claude the Architecture diagram and the grounding requirement from the project spec ("answer only from retrieved context, cite sources"). I will ask Claude to implement a generate_answer(query, chunks) function that builds a prompt containing the retrieved chunks and instructs the Groq LLM to answer only from that context, and a Gradio interface with a text input for the question and two text outputs for the answer and the sources list. I will verify grounding by asking a question my documents don't cover and confirming the system says it doesn't have enough information rather than hallucinating an answer.

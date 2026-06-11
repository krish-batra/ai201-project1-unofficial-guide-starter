"""
Milestone 5: Gradio Query Interface
Run with: python app.py
Then open http://localhost:7860 in your browser.
"""

import gradio as gr
from generate import generate_answer


def handle_query(question):
    """
    Takes a question string, runs the full RAG pipeline,
    and returns the answer and sources for display in Gradio.
    """
    if not question.strip():
        return "Please enter a question.", ""

    result = generate_answer(question)

    answer = result["answer"]
    sources = "\n".join(f"• {s}" for s in result["sources"])

    return answer, sources


# Build the Gradio UI
with gr.Blocks(title="Pitt CS Professor Guide") as demo:
    gr.Markdown("""
    # 🎓 Pitt CS Professor Unofficial Guide
    Ask questions about CS professors at the University of Pittsburgh based on real student reviews from Rate My Professors.
    
    **Example questions:**
    - Does Jarrett Billingsley allow AI on assignments?
    - Are Nick Farnan's exams open book?
    - How hard are Luis Oliveira's midterms?
    - Is John Ramirez's class good for beginners?
    - Is Patricia Quirin's CS0590 an easy class?
    """)

    with gr.Row():
        inp = gr.Textbox(
            label="Your Question",
            placeholder="Ask something about a Pitt CS professor...",
            lines=2
        )

    with gr.Row():
        btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_box = gr.Textbox(
            label="Answer",
            lines=8,
            interactive=False
        )

    with gr.Row():
        sources_box = gr.Textbox(
            label="Retrieved from",
            lines=3,
            interactive=False
        )

    # Trigger on button click or Enter key
    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])


if __name__ == "__main__":
    demo.launch()
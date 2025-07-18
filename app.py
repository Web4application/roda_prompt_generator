from core import get_combined_context, generate_roda_prompt
import gradio as gr

def generate_all(keyword, persona):
    context = get_combined_context(keyword)
    prompt = generate_roda_prompt(context_summary=context, persona_name=persona)
    return context, prompt

demo = gr.Interface(
    fn=generate_all,
    inputs=[
        gr.Textbox(label="Search Topic / Keyword", placeholder="e.g., Tim Cook, Sci-Fi AI"),
        gr.Textbox(label="Persona Name", value="Roda AI")
    ],
    outputs=[
        gr.Textbox(label="Scraped Web Context", lines=10),
        gr.Textbox(label="Generated System Prompt", lines=12)
    ],
    title="Roda Prompt Generator",
    description="Generate character-based AI system prompts using live search + GPT-4.",
)

demo.launch()
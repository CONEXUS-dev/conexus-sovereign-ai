"""Debug: test max_output_tokens with gemini-2.0-flash directly."""
import google.generativeai as genai

genai.configure(api_key="AIzaSyAtC3IPY8MDkFQBzei6SfdJIwdVYtvg2Ac")
gm = genai.GenerativeModel("gemini-2.0-flash")

# Simple test: ask for a long JSON array
prompt = "Output a JSON object with a key 'numbers' containing an array of integers from 0 to 199. Output ONLY the JSON, no other text."

for tokens in [256, 1024, 4096, 8192]:
    gc = genai.types.GenerationConfig(max_output_tokens=tokens, temperature=0.0)
    resp = gm.generate_content(prompt, generation_config=gc)
    fr = resp.candidates[0].finish_reason
    text_len = len(resp.text) if resp.text else 0
    print(f"max_output_tokens={tokens:5} -> text_len={text_len:5}  finish_reason={fr}")

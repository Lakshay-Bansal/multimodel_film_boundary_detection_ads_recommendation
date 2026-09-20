# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from huggingface_hub import login

hf_token = "..."
login(token=hf_token, add_to_git_credential=True)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B")

pipe = pipeline("text-generation", model=model)
pipe("Hey how are you doing today?")
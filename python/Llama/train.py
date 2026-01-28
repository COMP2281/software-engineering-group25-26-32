"""
{"messages":[
  {"role":"system","content":"You summarize text concisely."},
  {"role":"user","content":"Summarize this paragraph: 'Artificial Intelligence is transforming industries by automating tasks.'"},
  {"role":"assistant","content":"AI is changing industries by automating tasks."}
]}

{"messages":[
  {"role":"system","content":"Extract keywords from text."},
  {"role":"user","content":"Text: Neural networks are used for pattern recognition."},
  {"role":"assistant","content":"neural networks, pattern recognition, AI"}
]}

Examples of prompt structures for different tasks using a chat-based model.
""" 

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
import torch

# Load model and tokenizer
model_name = "meta-llama/Meta-Llama-3.1-8B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    device_map="auto"
)

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj","k_proj","v_proj","o_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Load dataset
dataset = load_dataset("json", data_files={"train":"train.jsonl","validation":"val.jsonl"})

# Tokenize function
def tokenize(example):
    return tokenizer(
        " ".join([m["content"] for m in example["messages"]]),
        truncation=True,
        max_length=512,
    )

dataset = dataset.map(tokenize, batched=True)

# Training
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./lora_output",
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=3,
    save_strategy="epoch",
    fp16=True,
    logging_steps=10,
    evaluation_strategy="epoch",
    save_total_limit=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    tokenizer=tokenizer,
)

trainer.train()

# Save LoRA adapter
model.save_pretrained("./lora_adapter")
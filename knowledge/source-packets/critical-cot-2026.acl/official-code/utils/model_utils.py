import torch
import argparse
from transformers import set_seed, AutoTokenizer, AutoModelForCausalLM, Mxfp4Config
from peft import LoraConfig, get_peft_model
from trl import DPOTrainer

class DPOTrainerNoRef(DPOTrainer):
    def __init__(self, *args, ref_scores=None, **kwargs):
        super().__init__(*args, ref_model=None, **kwargs)
        self.ref_scores_dict = {
            (ex["chosen"], ex["rejected"]): (ex["chosen_ref_score"], ex["rejected_ref_score"])
            for ex in ref_scores
        }

    def compute_reference_logps(self, batch):
        # Lookup precomputed scores
        chosen_texts = batch["chosen"]
        rejected_texts = batch["rejected"]
        ref_chosen_logps = []
        ref_rejected_logps = []

        for c, r in zip(chosen_texts, rejected_texts):
            c_score, r_score = self.ref_scores_dict[(c, r)]
            ref_chosen_logps.append(c_score)
            ref_rejected_logps.append(r_score)

        return torch.tensor(ref_chosen_logps, device=self.model.device), torch.tensor(ref_rejected_logps, device=self.model.device)


def precompute_ref_logits(dataset_dpo, base_model_name, tokenizer, save_path="ref_scores.pt"):
    """
    Precompute reference model logits for DPO training.
    """

    # Load reference model (can be CPU / quantized)
    ref_model, ref_tokenizer = load_model_and_tokenizer(base_model_name)
    ref_model.eval()
    ref_model.to("cuda" if torch.cuda.is_available() else "cpu")

    ref_scores = []

    for example in dataset_dpo:
        chosen = example["chosen"]
        rejected = example["rejected"]

        inputs_chosen = tokenizer(chosen, return_tensors="pt", truncation=True).to(ref_model.device)
        inputs_rejected = tokenizer(rejected, return_tensors="pt", truncation=True).to(ref_model.device)

        with torch.no_grad():
            # Get per-token logprobs
            logprobs_chosen = ref_model(**inputs_chosen).logits.log_softmax(-1)
            logprobs_rejected = ref_model(**inputs_rejected).logits.log_softmax(-1)

        # Compute sequence log-likelihood
        chosen_score = logprobs_chosen[:, :-1].gather(-1, inputs_chosen.input_ids[:, 1:].unsqueeze(-1)).sum().item()
        rejected_score = logprobs_rejected[:, :-1].gather(-1, inputs_rejected.input_ids[:, 1:].unsqueeze(-1)).sum().item()

        ref_scores.append({
            "chosen": chosen,
            "rejected": rejected,
            "chosen_ref_score": chosen_score,
            "rejected_ref_score": rejected_score,
        })

    torch.save(ref_scores, save_path)
    print(f"Saved reference scores to {save_path}")

def run_inference(model, tokenizer, system_prompt, user_prompt):
    """Run inference that works with both GPT-OSS and Qwen models."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Apply the right chat template
    try:
        input_ids = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)
    except Exception as e:
        print(f"apply_chat_template failed: {e}")
        # Fallback: just concatenate manually
        text = f"{system_prompt}\n{user_prompt}"
        input_ids = tokenizer(text, return_tensors="pt").to(model.device)

    gen_kwargs = dict(max_new_tokens=2048, do_sample=True, temperature=0.6)
    output_ids = model.generate(input_ids, **gen_kwargs)

    # Decode full text
    response = tokenizer.decode(output_ids[0], skip_special_tokens=False)

    # --- Handle GPT-OSS marker ---
    if "<|start|>assistant<|channel|>final<|message|>" in response:
        marker = "<|start|>assistant<|channel|>final<|message|>"
        response = response.split(marker, 1)[1].strip()
    # --- Handle Qwen / generic models ---
    elif "assistant" in tokenizer.chat_template or "user" in tokenizer.chat_template:
        # Qwen models already follow ChatML, decode normally
        response = tokenizer.decode(
            output_ids[0][input_ids.shape[1]:], skip_special_tokens=True
        )
        marker = "<think>\n</think>"
        response = response.replace("<think>","").replace("</think>","").strip()
    else:
        # Fallback: try trimming the input prefix
        response = tokenizer.decode(
            output_ids[0][input_ids.shape[1]:], skip_special_tokens=True
        ).strip()

    return response or ""


def load_model_and_tokenizer(base_model):
    assert torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    assert torch.cuda.device_count() > 0, "No CUDA devices found."

    print(f"Loading model {base_model}...")
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    quantized_config = Mxfp4Config(dequantize=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        attn_implementation="eager",
        torch_dtype=torch.bfloat16,
        quantization_config=quantized_config,
        use_cache=False,
        # device_map="auto",
    )
    return model, tokenizer


def wrap_model_with_LoRA(model, model_name):
    if "qwen" in model_name.lower():
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    elif "llama" in model_name.lower():
        target_modules = ["q_proj", "v_proj"]
    elif "gpt-oss" in model_name.lower():
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    else:
        raise ValueError(f"Unknown model type for LoRA: {model_name}")

    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=target_modules,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    peft_model = get_peft_model(model, peft_config)
    peft_model.print_trainable_parameters()
    return peft_model


def convert_to_messages(example):
    return {
        "messages": [
            {"role": "user", "content": example["question"]},
            {"role": "assistant", "content": example["preferred response"]},
        ]
    }

def convert_to_dpo_format(example):
    return {
        "prompt": example["question"],
        "chosen": example["preferred response"],
        "rejected": example["non-preferred response"]
    }
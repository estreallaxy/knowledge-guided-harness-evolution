"""GCG optimizer for LLMPrint fingerprint prompt construction."""

from __future__ import annotations

import copy
import gc
import logging
import string
from dataclasses import dataclass
from typing import List, Optional, Union

import torch
import transformers
from torch import Tensor
from transformers import set_seed

from nanogcg.utils import (
    find_executable_batch_size,
    get_nonascii_toks,
)


LOGGER = logging.getLogger("llmprint.gcg")
if not LOGGER.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)


@dataclass
class GCGConfig_target:
    num_steps: int = 1000
    optim_str_init: Union[str, List[str]] = "x x x x x x x x x x x x x x x x x x x x"
    search_width: int = 64
    batch_size: Optional[int] = None
    topk: int = 64
    n_replace: int = 1
    buffer_size: int = 0
    use_prefix_cache: bool = True
    allow_non_ascii: bool = False
    filter_ids: bool = True
    seed: Optional[int] = None
    verbosity: str = "INFO"
    target_word1: Optional[str] = None
    target_word2: Optional[str] = None
    alpha: float = 0.5
    beta: float = 1.0
    margin: float = 0.0


@dataclass
class GCGResult:
    best_loss: float
    best_string: str
    best_ids: Tensor
    losses: List[float]
    strings: List[str]


class AttackBuffer:
    def __init__(self, size: int):
        self.buffer = []
        self.size = size

    def add(self, loss: float, optim_ids: Tensor) -> None:
        if self.size == 0:
            self.buffer = [(loss, optim_ids)]
            return
        if len(self.buffer) < self.size:
            self.buffer.append((loss, optim_ids))
        else:
            self.buffer[-1] = (loss, optim_ids)
        self.buffer.sort(key=lambda x: x[0])

    def get_best_ids(self) -> Tensor:
        return self.buffer[0][1]

    def get_highest_loss(self) -> float:
        return self.buffer[-1][0]

    def log_buffer(self, tokenizer) -> None:
        message = "buffer:"
        for loss, ids in self.buffer:
            optim_str = tokenizer.batch_decode(ids)[0]
            optim_str = optim_str.replace("\\", "\\\\").replace("\n", "\\n")
            message += f"\nloss: {loss:.6f} | string: {optim_str}"
        LOGGER.info(message)


def custom_loss(
    first_token_logits: torch.Tensor,
    target_token1: int,
    target_token2: int,
    alpha: float,
    beta: float,
    margin: float,
) -> torch.Tensor:
    z_pos = first_token_logits[:, target_token1]
    z_neg = first_token_logits[:, target_token2]

    uniqueness = -torch.nn.functional.logsigmoid(z_pos - z_neg + margin)
    uniqueness = uniqueness + alpha * torch.abs(z_pos - z_neg)

    mask = torch.ones_like(first_token_logits, dtype=torch.bool)
    mask[:, target_token1] = False
    mask[:, target_token2] = False
    other_logits = first_token_logits.masked_fill(~mask, -torch.inf)
    max_other = torch.logsumexp(other_logits, dim=1)
    robustness = torch.nn.functional.relu(max_other - z_pos + margin)

    return uniqueness + beta * robustness


def _empty_cuda_cache() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def sample_ids_from_grad(
    ids: Tensor,
    grad: Tensor,
    search_width: int,
    topk: int,
    n_replace: int,
    not_allowed_ids: Optional[Tensor] = None,
) -> Tensor:
    n_optim_tokens = len(ids)
    original_ids = ids.repeat(search_width, 1)

    if not_allowed_ids is not None:
        grad[:, not_allowed_ids.to(grad.device)] = torch.inf

    topk_ids = (-grad).topk(topk, dim=1).indices
    sampled_ids_pos = torch.argsort(
        torch.rand((search_width, n_optim_tokens), device=grad.device),
        dim=1,
    )[:, :n_replace]
    sampled_ids_val = torch.gather(
        topk_ids[sampled_ids_pos],
        2,
        torch.randint(0, topk, (search_width, n_replace, 1), device=grad.device),
    ).squeeze(2)
    return original_ids.scatter_(1, sampled_ids_pos, sampled_ids_val)


def filter_ids(ids: Tensor, tokenizer: transformers.PreTrainedTokenizer) -> Tensor:
    ids_decoded = tokenizer.batch_decode(ids)
    filtered_ids = []
    for i, decoded in enumerate(ids_decoded):
        reencoded = tokenizer(
            decoded,
            add_special_tokens=False,
            return_tensors="pt",
        ).to(ids.device)["input_ids"][0]
        if torch.equal(ids[i], reencoded):
            filtered_ids.append(ids[i])
    if not filtered_ids:
        raise RuntimeError(
            "No token sequences remained unchanged after decode/re-encode. "
            "Try setting filter_ids=False or changing optim_str_init."
        )
    return torch.stack(filtered_ids)


class GCG:
    def __init__(
        self,
        model: transformers.PreTrainedModel,
        tokenizer: transformers.PreTrainedTokenizer,
        config: GCGConfig_target,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.model_device = next(model.parameters()).device
        self.embedding_layer = model.get_input_embeddings()
        self.not_allowed_ids = None
        if not config.allow_non_ascii:
            self.not_allowed_ids = get_nonascii_toks(tokenizer, device=self.model_device)

        if config.target_word1 is None or config.target_word2 is None:
            raise ValueError("Please specify target_word1 and target_word2 in GCGConfig_target.")

        target_ids = tokenizer(
            [config.target_word1, config.target_word2],
            add_special_tokens=False,
        )["input_ids"]
        if any(len(ids) != 1 for ids in target_ids):
            raise ValueError(
                "Each target word must correspond to exactly one tokenizer token."
            )
        self.target_token_ids = [ids[0] for ids in target_ids]
        self.before_embeds: Optional[Tensor] = None
        self.prefix_cache = None

        if model.dtype in (torch.float32, torch.float64) and self.model_device.type != "cpu":
            LOGGER.warning(
                "Model is in a full-precision dtype. Lower precision is usually much faster for GCG."
            )
        if self.model_device.type == "cpu":
            LOGGER.warning("Model is on CPU. Prompt optimization will be slow.")

    def run(self, prompt_template: str) -> GCGResult:
        if self.config.seed is not None:
            set_seed(self.config.seed)
            torch.use_deterministic_algorithms(True, warn_only=True)

        if prompt_template.count("{optim_str}") != 1:
            raise ValueError("prompt_template must contain exactly one '{optim_str}' placeholder.")

        before_str, _ = prompt_template.split("{optim_str}")
        before_ids = self.tokenizer(
            [before_str],
            add_special_tokens=False,
            padding=False,
            return_tensors="pt",
        )["input_ids"].to(self.model_device, torch.int64)

        if before_ids.shape[1] > 0:
            before_ids = before_ids[:, :-1]
        self.before_embeds = self.embedding_layer(before_ids)

        if self.config.use_prefix_cache and before_ids.shape[1] > 0:
            with torch.no_grad():
                outputs = self.model(input_ids=before_ids, use_cache=True)
                self.prefix_cache = outputs.past_key_values
                del outputs

        buffer = self.init_buffer()
        optim_ids = buffer.get_best_ids()

        losses: List[float] = []
        optim_strings: List[str] = []
        optim_ids_list: List[Tensor] = []

        for _ in range(self.config.num_steps):
            optim_ids_onehot_grad = self.compute_token_gradient(optim_ids)
            with torch.no_grad():
                sampled_ids = sample_ids_from_grad(
                    optim_ids.squeeze(0),
                    optim_ids_onehot_grad.squeeze(0),
                    self.config.search_width,
                    self.config.topk,
                    self.config.n_replace,
                    not_allowed_ids=self.not_allowed_ids,
                )
                if self.config.filter_ids:
                    sampled_ids = filter_ids(sampled_ids, self.tokenizer)
                new_search_width = sampled_ids.shape[0]
                if self.prefix_cache is not None:
                    input_embeds = self.embedding_layer(sampled_ids)
                else:
                    assert self.before_embeds is not None
                    input_embeds = torch.cat(
                        [self.before_embeds.repeat(new_search_width, 1, 1), self.embedding_layer(sampled_ids)],
                        dim=1,
                    )
                loss = find_executable_batch_size(
                    self._compute_candidates_loss,
                    self.config.batch_size or new_search_width,
                )(input_embeds)
                current_loss = loss.min().item()
                optim_ids = sampled_ids[loss.argmin()].unsqueeze(0)
                losses.append(current_loss)
                if self.config.buffer_size == 0 or current_loss < buffer.get_highest_loss():
                    buffer.add(current_loss, optim_ids)

            optim_ids = buffer.get_best_ids()
            optim_str = self.tokenizer.batch_decode(optim_ids)[0]
            optim_strings.append(optim_str)
            optim_ids_list.append(optim_ids.detach().clone())
            if self.config.buffer_size > 0:
                buffer.log_buffer(self.tokenizer)

        min_loss_index = losses.index(min(losses))
        return GCGResult(
            best_loss=losses[min_loss_index],
            best_string=optim_strings[min_loss_index],
            best_ids=optim_ids_list[min_loss_index],
            losses=losses,
            strings=optim_strings,
        )

    def init_buffer(self) -> AttackBuffer:
        LOGGER.info("Initializing attack buffer...")
        buffer = AttackBuffer(self.config.buffer_size)

        if isinstance(self.config.optim_str_init, str):
            init_optim_ids = self.tokenizer(
                self.config.optim_str_init,
                add_special_tokens=False,
                return_tensors="pt",
            )["input_ids"].to(self.model_device)
            if self.config.buffer_size > 1:
                init_chars = self.tokenizer(
                    list(string.ascii_lowercase),
                    add_special_tokens=False,
                    return_tensors="pt",
                )["input_ids"].squeeze().to(self.model_device)
                init_indices = torch.randint(
                    0,
                    init_chars.shape[0],
                    (self.config.buffer_size - 1, init_optim_ids.shape[1]),
                )
                init_buffer_ids = torch.cat([init_optim_ids, init_chars[init_indices]], dim=0)
            else:
                init_buffer_ids = init_optim_ids
        else:
            if self.config.buffer_size > 0 and len(self.config.optim_str_init) != self.config.buffer_size:
                LOGGER.warning(
                    "Using %d initializations but buffer_size=%d.",
                    len(self.config.optim_str_init),
                    self.config.buffer_size,
                )
            init_buffer_ids = self.tokenizer(
                self.config.optim_str_init,
                add_special_tokens=False,
                return_tensors="pt",
            )["input_ids"].to(self.model_device)

        true_buffer_size = init_buffer_ids.shape[0] if self.config.buffer_size == 0 else max(1, self.config.buffer_size)
        if self.prefix_cache is not None:
            init_buffer_embeds = self.embedding_layer(init_buffer_ids)
        else:
            assert self.before_embeds is not None
            init_buffer_embeds = torch.cat(
                [self.before_embeds.repeat(true_buffer_size, 1, 1), self.embedding_layer(init_buffer_ids)],
                dim=1,
            )

        init_losses = find_executable_batch_size(
            self._compute_candidates_loss,
            self.config.batch_size or true_buffer_size,
        )(init_buffer_embeds)

        for i in range(true_buffer_size):
            buffer.add(float(init_losses[i].item()), init_buffer_ids[[i]])

        if self.config.buffer_size > 0:
            buffer.log_buffer(self.tokenizer)
        LOGGER.info("Attack buffer initialized.")
        return buffer

    def compute_token_gradient(self, optim_ids: Tensor) -> Tensor:
        optim_ids_onehot = torch.nn.functional.one_hot(
            optim_ids,
            num_classes=self.embedding_layer.num_embeddings,
        ).to(self.model_device, self.model.dtype)
        optim_ids_onehot.requires_grad_()

        optim_embeds = optim_ids_onehot @ self.embedding_layer.weight
        if self.prefix_cache is not None:
            outputs = self.model(
                inputs_embeds=optim_embeds,
                past_key_values=self.prefix_cache,
                use_cache=True,
            )
        else:
            assert self.before_embeds is not None
            input_embeds = torch.cat([self.before_embeds, optim_embeds], dim=1)
            outputs = self.model(inputs_embeds=input_embeds)

        first_token_logits = outputs.logits[:, -1, :]
        loss = custom_loss(
            first_token_logits,
            self.target_token_ids[0],
            self.target_token_ids[1],
            alpha=self.config.alpha,
            beta=self.config.beta,
            margin=self.config.margin,
        )
        grad = torch.autograd.grad(outputs=[loss], inputs=[optim_ids_onehot])[0]
        del outputs
        return grad

    def _compute_candidates_loss(self, search_batch_size: int, input_embeds: Tensor) -> Tensor:
        all_loss = []
        for i in range(0, input_embeds.shape[0], search_batch_size):
            with torch.no_grad():
                batch_embeds = input_embeds[i:i + search_batch_size]
                current_batch_size = batch_embeds.shape[0]
                if self.prefix_cache is not None:
                    outputs = self.model(
                        inputs_embeds=batch_embeds,
                        past_key_values=self.prefix_cache,
                        use_cache=True,
                    )
                else:
                    outputs = self.model(inputs_embeds=batch_embeds)
                first_token_logits = outputs.logits[:, -1, :]
                loss = custom_loss(
                    first_token_logits,
                    self.target_token_ids[0],
                    self.target_token_ids[1],
                    alpha=self.config.alpha,
                    beta=self.config.beta,
                    margin=self.config.margin,
                )
                loss = loss * torch.ones(current_batch_size, device=loss.device)
                all_loss.append(loss)
                del outputs
                gc.collect()
                _empty_cuda_cache()
        return torch.cat(all_loss, dim=0)


def run(
    model: transformers.PreTrainedModel,
    tokenizer: transformers.PreTrainedTokenizer,
    prompt_template: str,
    config: GCGConfig_target,
) -> GCGResult:
    LOGGER.setLevel(getattr(logging, config.verbosity.upper(), logging.INFO))
    gcg = GCG(model, tokenizer, config)
    return gcg.run(prompt_template)

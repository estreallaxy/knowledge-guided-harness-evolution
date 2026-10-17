import argparse
import logging
import os
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_TASK_CONFIGS = [
    str(REPO_ROOT / "aoeb_ng/tasks/MMRC-R-session-it-pair.json"),
    str(REPO_ROOT / "aoeb_ng/tasks/MMRC-R-session-vision-doc.json"),
    str(REPO_ROOT / "aoeb_ng/tasks/MMRC-R-round-it-pair.json"),
]

DEFAULT_VLM2VEC2_PATH = os.environ.get("AOEB_VLM2VEC2_PATH", "VLM2Vec/VLM2Vec-V2.0")
DEFAULT_VLM2VEC2_BASE_PATH = os.environ.get(
    "AOEB_VLM2VEC2_BASE_PATH",
    "Qwen/Qwen2-VL-2B-Instruct",
)
DEFAULT_VLM2VEC_LORA_PATH = os.environ.get(
    "AOEB_VLM2VEC_LORA_PATH",
    "TIGER-Lab/VLM2Vec-LoRA",
)
DEFAULT_VLM2VEC_LORA_BASE_PATH = (
    os.environ.get("AOEB_VLM2VEC_LORA_BASE_PATH", "microsoft/Phi-3.5-vision-instruct")
)
DEFAULT_QWEN3_VL_EMBEDDING_2B_PATH = (
    os.environ.get(
        "AOEB_QWEN3_VL_EMBEDDING_2B_PATH",
        "Qwen/Qwen3-VL-Embedding-2B",
    )
)
DEFAULT_JINA_V4_PATH = os.environ.get(
    "AOEB_JINA_V4_PATH",
    "jinaai/jina-embeddings-v4",
)
DEFAULT_GME_2B_PATH = os.environ.get(
    "AOEB_GME_2B_PATH",
    "Alibaba-NLP/gme-Qwen2-VL-2B-Instruct",
)
DEFAULT_GME_7B_PATH = os.environ.get(
    "AOEB_GME_7B_PATH",
    "Alibaba-NLP/gme-Qwen2-VL-7B-Instruct",
)
DEFAULT_MME5_PATH = os.environ.get(
    "AOEB_MME5_PATH",
    "intfloat/mmE5-mllama-11b-instruct",
)
DEFAULT_VISTA_BASE_PATH = os.environ.get(
    "AOEB_VISTA_BASE_PATH",
    "BAAI/bge-base-en-v1.5",
)
DEFAULT_VISTA_BASE_WEIGHT_PATH = os.environ.get(
    "AOEB_VISTA_BASE_WEIGHT_PATH",
    "Visualized_base_en_v1.5.pth",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run AOEB retrieval tasks from JSON configs."
    )
    parser.add_argument("--model", required=True, help="Model name or local path.")
    parser.add_argument(
        "--task-configs",
        default=",".join(DEFAULT_TASK_CONFIGS),
        help="Comma-separated AOEB task config paths. Empty uses MMRC-R defaults.",
    )
    parser.add_argument("--output-dir", default="./results")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--gpu-id", default="0")
    parser.add_argument("--max-length", type=int, default=8192)
    return parser.parse_args()


def setup_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s|%(name)s:%(lineno)s|%(levelname)s - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        level=logging.INFO,
    )


def parse_task_configs(task_configs_arg: str) -> list[str]:
    task_configs = [
        path.strip() for path in task_configs_arg.split(",") if path.strip()
    ]
    return task_configs or DEFAULT_TASK_CONFIGS


def model_tag(model_name: str) -> str:
    tag = Path(model_name).name or model_name
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", tag)


def build_model(model_name: str, device: str, max_length: int):
    import torch

    from aoeb_ng.models.gme import GmeQwen2VL
    from aoeb_ng.models.jinav4 import JinaV4Wrapper
    from aoeb_ng.models.mme5 import MME5
    from aoeb_ng.models.qwen3vl_embed import Qwen3VLEmbeddingWrapper
    from aoeb_ng.models.vista import vista_loader
    from aoeb_ng.models.vlm2vec import VLM2VecWrapper
    from aoeb_ng.util import get_model

    logger = logging.getLogger("run_batch_aoeb")

    if (
        model_name in {"vista", "vista-base", "bge-visualized-base"}
        or "bge-base-en-v1.5" in model_name
    ):
        model_path = (
            DEFAULT_VISTA_BASE_PATH
            if model_name in {"vista", "vista-base", "bge-visualized-base"}
            else model_name
        )
        vista_max_length = 512
        image_tokens_num = 196
        logger.info(
            "Loading VISTA from %s with weight %s, max_length=%d, "
            "image_tokens_num=%d, use_instruction=False",
            model_path,
            DEFAULT_VISTA_BASE_WEIGHT_PATH,
            vista_max_length,
            image_tokens_num,
        )
        model = vista_loader(
            model_path,
            model_weight=DEFAULT_VISTA_BASE_WEIGHT_PATH,
            image_tokens_num=image_tokens_num,
        )
        model.tokenizer.model_max_length = vista_max_length
        model.image_tokens_num = image_tokens_num
        model.max_text_len_with_image = vista_max_length - image_tokens_num
        return model

    if (
        model_name in {"jina-v4", "jina-embeddings-v4"}
        or "jina-embeddings-v4" in model_name
    ):
        model_path = (
            DEFAULT_JINA_V4_PATH
            if model_name in {"jina-v4", "jina-embeddings-v4"}
            else model_name
        )
        logger.info(
            "Loading Jina embeddings v4 from %s with max_length=%d",
            model_path,
            max_length,
        )
        model = JinaV4Wrapper(
            model_path,
            max_length=max_length,
            device_map="cuda",
            attn_implementation="flash_attention_2",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        model.model.task = "retrieval"
        return model

    if (
        model_name in {"gme2b", "gme-2b", "gme-qwen2-vl-2b"}
        or "gme-Qwen2-VL-2B-Instruct" in model_name
    ):
        model_path = (
            DEFAULT_GME_2B_PATH
            if model_name in {"gme2b", "gme-2b", "gme-qwen2-vl-2b"}
            else model_name
        )
        logger.info(
            "Loading GME Qwen2-VL-2B from %s with max_length=%d",
            model_path,
            max_length,
        )
        return GmeQwen2VL(
            "Alibaba-NLP/gme-Qwen2-VL-2B-Instruct",
            model_path=model_path,
            revision="main",
            device=device,
            max_length=max_length,
            attn_implementation="flash_attention_2",
        )

    if (
        model_name in {"gme7b", "gme-7b", "gme-qwen2-vl-7b"}
        or "gme-Qwen2-VL-7B-Instruct" in model_name
    ):
        model_path = (
            DEFAULT_GME_7B_PATH
            if model_name in {"gme7b", "gme-7b", "gme-qwen2-vl-7b"}
            else model_name
        )
        logger.info(
            "Loading GME Qwen2-VL-7B from %s with max_length=%d",
            model_path,
            max_length,
        )
        return GmeQwen2VL(
            "Alibaba-NLP/gme-Qwen2-VL-7B-Instruct",
            model_path=model_path,
            revision="main",
            device=device,
            max_length=max_length,
            attn_implementation="flash_attention_2",
        )

    if (
        model_name in {"mme5", "mme5-mllama", "mmE5-mllama-11b-instruct"}
        or "mmE5-mllama-11b-instruct" in model_name
        or "mme5" in model_name.lower()
    ):
        model_path = (
            DEFAULT_MME5_PATH
            if model_name in {"mme5", "mme5-mllama", "mmE5-mllama-11b-instruct"}
            else model_name
        )
        logger.info(
            "Loading mmE5 mllama from %s with max_length=%d and use_default_prompt=False",
            model_path,
            max_length,
        )
        return MME5(
            model_path,
            device=device,
            max_length=max_length,
            use_default_prompt=False,
            trust_remote_code=True,
        )

    if model_name == "vlm2vec2" or "VLM2Vec-V2.0" in model_name:
        model_path = (
            DEFAULT_VLM2VEC2_PATH if model_name == "vlm2vec2" else model_name
        )
        logger.info(
            "Loading VLM2Vec2 from %s with base %s and max_length=%d",
            model_path,
            DEFAULT_VLM2VEC2_BASE_PATH,
            max_length,
        )
        return VLM2VecWrapper(
            model_path,
            base_model_name=DEFAULT_VLM2VEC2_BASE_PATH,
            device=device,
            max_length=max_length,
        )

    if (
        model_name in {"vlm2vec", "vlm2vec-lora", "vlm2vec-v1"}
        or "VLM2Vec-LoRA" in model_name
    ):
        model_path = (
            DEFAULT_VLM2VEC_LORA_PATH
            if model_name in {"vlm2vec", "vlm2vec-lora", "vlm2vec-v1"}
            else model_name
        )
        logger.info(
            "Loading first-gen VLM2Vec-LoRA from %s with base %s and max_length=%d",
            model_path,
            DEFAULT_VLM2VEC_LORA_BASE_PATH,
            max_length,
        )
        return VLM2VecWrapper(
            model_path,
            base_model_name=DEFAULT_VLM2VEC_LORA_BASE_PATH,
            device=device,
            max_length=max_length,
        )

    if (
        model_name in {"qwen3-vl-2b", "qwen3-vl-embedding-2b"}
        or "Qwen3-VL-Embedding-2B" in model_name
    ):
        model_path = (
            DEFAULT_QWEN3_VL_EMBEDDING_2B_PATH
            if model_name in {"qwen3-vl-2b", "qwen3-vl-embedding-2b"}
            else model_name
        )
        logger.info(
            "Loading Qwen3-VL-Embedding-2B from %s with max_length=%d",
            model_path,
            max_length,
        )
        return Qwen3VLEmbeddingWrapper(
            model_path,
            device=device,
            attn_implementation="flash_attention_2",
            max_length=max_length,
        )

    logger.info("Loading %s through aoeb_ng.util.get_model", model_name)
    return get_model(model_name, device)


def main() -> None:
    args = parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_id
    setup_logging()

    import torch

    from aoeb_ng.task import RetrievalTask

    logger = logging.getLogger("run_batch_aoeb")
    task_configs = parse_task_configs(args.task_configs)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tag = model_tag(args.model)
    output_dir = str(Path(args.output_dir) / tag)

    logger.info("Model: %s", args.model)
    logger.info("Model tag: %s", tag)
    logger.info("CUDA_VISIBLE_DEVICES: %s", os.environ["CUDA_VISIBLE_DEVICES"])
    logger.info("Device: %s", device)
    logger.info("Task configs: %s", ", ".join(task_configs))
    logger.info("Output dir: %s", output_dir)
    logger.info("Batch size: %d", args.batch_size)
    logger.info("Max length: %d", args.max_length)

    model = build_model(args.model, device, args.max_length)
    encode_kwargs = {"batch_size": args.batch_size}

    for task_config in task_configs:
        logger.info("Evaluating task config: %s", task_config)
        task = RetrievalTask.from_config(task_config)
        task.evaluate(model, output_dir, encode_kwargs=encode_kwargs)

    logger.info("Done %d task(s).", len(task_configs))


if __name__ == "__main__":
    main()

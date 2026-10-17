import argparse
import logging
import os
import sys
from collections.abc import Callable
from copy import deepcopy

import torch
import mteb
from mteb.cache import ResultCache
from mteb.models.model_implementations.bge_models import bge_large_en_v1_5, bge_m3
from mteb.models.model_implementations.e5_instruct import e5_instruct, e5_mistral
from mteb.models.model_implementations.gte_models import gte_multilingual_base
from mteb.models.model_implementations.jina_models import jina_embeddings_v4
from mteb.models.model_implementations.mme5_models import mme5_mllama
from mteb.models.model_implementations.nomic_models import nomic_embed_text_v2_moe
from mteb.models.model_implementations.nvidia_models import NV_embed_v2
from mteb.models.model_implementations.qwen3_vl_embedding_models import (
    Qwen3VLEmbeddingWrapper,
)
from mteb.models.model_implementations.qwen3_models import q3e_instruct_loader
from mteb.models.model_implementations.vista_models import visualized_bge_base


os.environ.setdefault("HF_HOME", ".cache/huggingface")
os.environ.setdefault("HF_DATASETS_CACHE", ".cache/huggingface/datasets")
os.environ.setdefault("MTEB_CACHE", ".cache/mteb")


logging.basicConfig(
    format="%(asctime)s|%(name)s:%(lineno)s|%(levelname)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
)
logger = logging.getLogger("run_batch_mteb")


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
DEFAULT_QWEN3_EMBEDDING_8B_PATH = os.environ.get(
    "AOEB_QWEN3_EMBEDDING_8B_PATH",
    "Qwen/Qwen3-Embedding-8B",
)
DEFAULT_JINA_V4_PATH = os.environ.get("AOEB_JINA_V4_PATH", "jinaai/jina-embeddings-v4")
DEFAULT_GME_2B_PATH = os.environ.get(
    "AOEB_GME_2B_PATH",
    "Alibaba-NLP/gme-Qwen2-VL-2B-Instruct",
)
DEFAULT_GME_7B_PATH = os.environ.get(
    "AOEB_GME_7B_PATH",
    "Alibaba-NLP/gme-Qwen2-VL-7B-Instruct",
)
DEFAULT_MME5_PATH = os.environ.get("AOEB_MME5_PATH", "intfloat/mmE5-mllama-11b-instruct")
DEFAULT_NV_EMBED_V2_PATH = os.environ.get("AOEB_NV_EMBED_V2_PATH", "nvidia/NV-Embed-v2")
DEFAULT_ME5_INSTRUCT_PATH = (
    os.environ.get(
        "AOEB_ME5_INSTRUCT_PATH",
        "intfloat/multilingual-e5-large-instruct",
    )
)
DEFAULT_E5_MISTRAL_PATH = os.environ.get(
    "AOEB_E5_MISTRAL_PATH",
    "intfloat/e5-mistral-7b-instruct",
)
DEFAULT_NOMIC_EMBED_TEXT_V2_MOE_PATH = (
    os.environ.get(
        "AOEB_NOMIC_EMBED_TEXT_V2_MOE_PATH",
        "nomic-ai/nomic-embed-text-v2-moe",
    )
)
DEFAULT_MGTE_PATH = os.environ.get("AOEB_MGTE_PATH", "Alibaba-NLP/gte-multilingual-base")
DEFAULT_BGE_M3_PATH = os.environ.get("AOEB_BGE_M3_PATH", "BAAI/bge-m3")
DEFAULT_BGE_LARGE_EN_V1_5_PATH = (
    os.environ.get("AOEB_BGE_LARGE_EN_V1_5_PATH", "BAAI/bge-large-en-v1.5")
)
DEFAULT_VISTA_BASE_PATH = os.environ.get("AOEB_VISTA_BASE_PATH", "BAAI/bge-base-en-v1.5")
DEFAULT_VISTA_BASE_WEIGHT_PATH = (
    os.environ.get("AOEB_VISTA_BASE_WEIGHT_PATH", "Visualized_base_en_v1.5.pth")
)
VISTA_BASE_ALIASES = {"vista", "vista-base", "bge-visualized-base"}
MME5_ALIASES = {"mme5", "mme5-mllama", "mmE5-mllama-11b-instruct"}
QWEN3_EMBEDDING_8B_ALIASES = {"qwen3-embedding-8b", "Qwen3-Embedding-8B"}
NV_EMBED_V2_ALIASES = {"nv-embed-v2", "nvembed", "NV-Embed-v2"}
ME5_INSTRUCT_ALIASES = {
    "me5",
    "m-e5",
    "multilingual-e5-large-instruct",
    "intfloat/multilingual-e5-large-instruct",
}
E5_MISTRAL_ALIASES = {
    "e5-mistral",
    "e5-mistral-7b-instruct",
    "intfloat/e5-mistral-7b-instruct",
}
NOMIC_EMBED_TEXT_V2_MOE_ALIASES = {
    "nomic",
    "nomic-v2-moe",
    "nomic-embed-text-v2-moe",
}
MGTE_ALIASES = {
    "mgte",
    "m-gte",
    "gte-multilingual-base",
    "Alibaba-NLP/gte-multilingual-base",
}
BGE_M3_ALIASES = {
    "bge-m3",
    "BAAI/bge-m3",
}
BGE_LARGE_EN_V1_5_ALIASES = {
    "bge-large-en-v1.5",
    "BAAI/bge-large-en-v1.5",
}


def build_model(
    model_arg: str,
    max_length: int | None = None,
    use_vista_task_prompt: bool = False,
    use_bge_m3_task_prompt: bool = False,
    use_bge_large_task_prompt: bool = False,
    use_nomic_task_prompt: bool = False,
):
    import mteb_patch.load_data  # noqa: F401
    from mteb_patch.models.bge_large_en_v1_5 import (
        AOEBBGELargeEnV15Wrapper,
        bge_large_en_v1_5_model_meta,
    )
    from mteb_patch.models.bge_m3 import AOEBBGEM3Wrapper, bge_m3_model_meta
    from mteb_patch.models.gme import AOEBGmeQwen2VLWrapper
    from mteb_patch.models.e5_mistral import AOEBE5MistralWrapper
    from mteb_patch.models.jina_v4 import AOEBJinaV4Wrapper
    from mteb_patch.models.me5_instruct import AOEBME5InstructWrapper
    from mteb_patch.models.mgte import AOEBMGTEWrapper
    from mteb_patch.models.mme5 import AOEBMME5Wrapper
    from mteb_patch.models.nomic import AOEBNomicWrapper, nomic_model_meta
    from mteb_patch.models.nvembed import AOEBNVEmbedWrapper
    from mteb_patch.models.vista import AOEBVistaWrapper, vista_model_meta
    from mteb_patch.models.vlm2vec_v1 import (
        FirstGenVLM2VecLoRAWrapper,
        vlm2vec_lora,
    )
    from mteb_patch.models.vlm2vec_v2 import (
        VLM2VecWrapper as AOEBVLM2Vec2Wrapper,
    )

    if model_arg in VISTA_BASE_ALIASES or "bge-base-en-v1.5" in model_arg:
        model_path = DEFAULT_VISTA_BASE_PATH if model_arg in VISTA_BASE_ALIASES else model_arg
        vista_max_length = 512
        logger.info(
            "Loading VISTA bge-base from %s with weight %s, max_length=%d, "
            "use_task_prompt=%s",
            model_path,
            DEFAULT_VISTA_BASE_WEIGHT_PATH,
            vista_max_length,
            use_vista_task_prompt,
        )
        model = AOEBVistaWrapper(
            model_name=model_path,
            model_weight=DEFAULT_VISTA_BASE_WEIGHT_PATH,
            image_tokens_num=196,
            max_length=vista_max_length,
            torch_dtype=torch.float16,
            use_task_prompt=use_vista_task_prompt,
        )
        model.mteb_model_meta = vista_model_meta(
            visualized_bge_base,
            use_task_prompt=use_vista_task_prompt,
        )
        return model

    if model_arg in {"jina-v4", "jina-embeddings-v4"} or "jina-embeddings-v4" in model_arg:
        model_path = (
            DEFAULT_JINA_V4_PATH
            if model_arg in {"jina-v4", "jina-embeddings-v4"}
            else model_arg
        )
        logger.info("Loading Jina embeddings v4 from %s", model_path)
        model = AOEBJinaV4Wrapper(
            model_path,
            device_map="cuda",
            attn_implementation="flash_attention_2",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        model.mteb_model_meta = jina_embeddings_v4
        return model

    if (
        model_arg in MME5_ALIASES
        or "mmE5-mllama-11b-instruct" in model_arg
        or "mme5" in model_arg.lower()
    ):
        model_path = DEFAULT_MME5_PATH if model_arg in MME5_ALIASES else model_arg
        mme5_max_length = 8192
        logger.info(
            "Loading mmE5 mllama from %s with max_seq_length=%d",
            model_path,
            mme5_max_length,
        )
        model = AOEBMME5Wrapper(
            model_path,
            device="cuda",
            trust_remote_code=True,
            model_kwargs={"torch_dtype": torch.bfloat16},
            max_seq_length=mme5_max_length,
        )
        model.mteb_model_meta = deepcopy(mme5_mllama)
        model.mteb_model_meta.max_tokens = mme5_max_length
        return model

    if (
        model_arg in {"vlm2vec-lora", "vlm2vec", "vlm2vec-v1"}
        or "VLM2Vec-LoRA" in model_arg
    ):
        model_path = (
            DEFAULT_VLM2VEC_LORA_PATH
            if model_arg in {"vlm2vec-lora", "vlm2vec", "vlm2vec-v1"}
            else model_arg
        )
        vlm2vec_max_length = 8192 if max_length is None else max_length
        logger.info(
            "Loading first-gen VLM2Vec-LoRA from %s with base %s and max_length=%d",
            model_path,
            DEFAULT_VLM2VEC_LORA_BASE_PATH,
            vlm2vec_max_length,
        )
        model = FirstGenVLM2VecLoRAWrapper(
            model_name=model_path,
            base_model_name=DEFAULT_VLM2VEC_LORA_BASE_PATH,
            device="cuda",
            max_length=vlm2vec_max_length,
            torch_dtype=torch.bfloat16,
        )
        model.mteb_model_meta = vlm2vec_lora
        return model

    if model_arg == "vlm2vec2" or "VLM2Vec-V2.0" in model_arg:
        model_path = DEFAULT_VLM2VEC2_PATH if model_arg == "vlm2vec2" else model_arg
        logger.info("Loading VLM2Vec2 from %s", model_path)
        model = AOEBVLM2Vec2Wrapper(
            model_name=model_path,
            base_model_name=DEFAULT_VLM2VEC2_BASE_PATH,
            max_length=4096 if max_length is None else max_length,
        )
        model.mteb_model_meta = mteb.get_model_meta("TIGER-Lab/VLM2Vec-LoRA")
        model.mteb_model_meta.name = "VLM2Vec/VLM2Vec-V2.0"
        return model

    if model_arg == "qwen3-vl-embedding-2b" or "Qwen3-VL-Embedding-2B" in model_arg:
        model_path = (
            DEFAULT_QWEN3_VL_EMBEDDING_2B_PATH
            if model_arg == "qwen3-vl-embedding-2b"
            else model_arg
        )
        logger.info("Loading Qwen3-VL-Embedding-2B from %s", model_path)
        model = Qwen3VLEmbeddingWrapper(
            model_path,
            device="cuda",
            attn_implementation="flash_attention_2",
            torch_dtype=torch.bfloat16,
            max_length=8192
        )
        model.mteb_model_meta = mteb.get_model_meta("Qwen/Qwen3-VL-Embedding-2B")
        return model

    if (
        model_arg in QWEN3_EMBEDDING_8B_ALIASES
        or "Qwen3-Embedding-8B" in model_arg
        or "qwen3-embedding-8b" in model_arg.lower()
    ):
        model_path = (
            DEFAULT_QWEN3_EMBEDDING_8B_PATH
            if model_arg in QWEN3_EMBEDDING_8B_ALIASES
            else model_arg
        )
        qwen3_max_length = 8192
        logger.info(
            "Loading Qwen3-Embedding-8B from %s with max_seq_length=%d",
            model_path,
            qwen3_max_length,
        )
        model = q3e_instruct_loader(
            model_path,
            revision="main",
            device="cuda",
            max_seq_length=qwen3_max_length,
            model_kwargs={
                "attn_implementation": "flash_attention_2",
                "torch_dtype": torch.float16,
            },
        )
        model.mteb_model_meta = deepcopy(
            mteb.get_model_meta("Qwen/Qwen3-Embedding-8B")
        )
        model.mteb_model_meta.max_tokens = qwen3_max_length
        return model

    if (
        model_arg in NV_EMBED_V2_ALIASES
        or "nv-embed-v2" in model_arg.lower()
    ):
        model_path = (
            DEFAULT_NV_EMBED_V2_PATH
            if model_arg in NV_EMBED_V2_ALIASES
            else model_arg
        )
        nv_embed_max_length = 8192 if max_length is None else max_length
        logger.info(
            "Loading NV-Embed-v2 from %s with max_length=%d",
            model_path,
            nv_embed_max_length,
        )
        model = AOEBNVEmbedWrapper(
            model_path,
            device="cuda",
            max_length=nv_embed_max_length,
            torch_dtype=torch.float16,
            attn_implementation="flash_attention_2",
        )
        model.mteb_model_meta = deepcopy(NV_embed_v2)
        model.mteb_model_meta.max_tokens = nv_embed_max_length
        return model

    if (
        model_arg in ME5_INSTRUCT_ALIASES
        or "multilingual-e5-large-instruct" in model_arg
    ):
        model_path = (
            DEFAULT_ME5_INSTRUCT_PATH
            if model_arg in ME5_INSTRUCT_ALIASES
            else model_arg
        )
        me5_max_length = 512 if max_length is None else max_length
        logger.info(
            "Loading multilingual-e5-large-instruct from %s with max_seq_length=%d",
            model_path,
            me5_max_length,
        )
        model = AOEBME5InstructWrapper(
            model_name=model_path,
            revision=None,
            device="cuda",
            max_seq_length=me5_max_length,
            torch_dtype=torch.float16,
        )
        model.mteb_model_meta = deepcopy(e5_instruct)
        model.mteb_model_meta.max_tokens = me5_max_length
        return model

    if (
        model_arg in E5_MISTRAL_ALIASES
        or "e5-mistral-7b-instruct" in model_arg.lower()
    ):
        model_path = (
            DEFAULT_E5_MISTRAL_PATH
            if model_arg in E5_MISTRAL_ALIASES
            else model_arg
        )
        e5_mistral_max_length = 8192 if max_length is None else max_length
        logger.info(
            "Loading e5-mistral-7b-instruct from %s with max_seq_length=%d",
            model_path,
            e5_mistral_max_length,
        )
        model = AOEBE5MistralWrapper(
            model_name=model_path,
            revision=None,
            device="cuda",
            instruction_template=e5_mistral.loader_kwargs["instruction_template"],
            max_seq_length=e5_mistral_max_length,
            apply_instruction_to_passages=False,
            model_kwargs={"dtype": torch.float16},
        )
        model.mteb_model_meta = deepcopy(e5_mistral)
        model.mteb_model_meta.max_tokens = e5_mistral_max_length
        return model

    if (
        model_arg in NOMIC_EMBED_TEXT_V2_MOE_ALIASES
        or "nomic-embed-text-v2-moe" in model_arg.lower()
    ):
        model_path = (
            DEFAULT_NOMIC_EMBED_TEXT_V2_MOE_PATH
            if model_arg in NOMIC_EMBED_TEXT_V2_MOE_ALIASES
            else model_arg
        )
        nomic_max_length = 512
        logger.info(
            "Loading nomic-embed-text-v2-moe from %s with max_seq_length=%d, "
            "use_task_prompt=%s",
            model_path,
            nomic_max_length,
            use_nomic_task_prompt,
        )
        model = AOEBNomicWrapper(
            model_name=model_path,
            revision=None,
            device="cuda",
            trust_remote_code=True,
            local_files_only=True,
            max_seq_length=nomic_max_length,
            use_task_prompt=use_nomic_task_prompt,
            model_kwargs={"torch_dtype": torch.bfloat16},
        )
        model.mteb_model_meta = nomic_model_meta(
            nomic_embed_text_v2_moe,
            use_task_prompt=use_nomic_task_prompt,
        )
        model.mteb_model_meta.max_tokens = nomic_max_length
        return model

    if (
        model_arg in MGTE_ALIASES
        or "gte-multilingual-base" in model_arg
    ):
        model_path = DEFAULT_MGTE_PATH if model_arg in MGTE_ALIASES else model_arg
        mgte_max_length = 8192
        logger.info(
            "Loading mGTE from %s with max_seq_length=%d",
            model_path,
            mgte_max_length,
        )
        model = AOEBMGTEWrapper(
            model_path,
            device="cuda",
            max_seq_length=mgte_max_length,
            torch_dtype=torch.float16,
        )
        model.mteb_model_meta = deepcopy(gte_multilingual_base)
        model.mteb_model_meta.max_tokens = mgte_max_length
        return model

    if (
        model_arg in BGE_M3_ALIASES
        or "bge-m3" in model_arg
    ):
        model_path = DEFAULT_BGE_M3_PATH if model_arg in BGE_M3_ALIASES else model_arg
        bge_m3_max_length = 8192 if max_length is None else max_length
        logger.info(
            "Loading bge-m3 from %s with max_seq_length=%d",
            model_path,
            bge_m3_max_length,
        )
        model = AOEBBGEM3Wrapper(
            model_path,
            device="cuda",
            max_seq_length=bge_m3_max_length,
            torch_dtype=torch.float16,
            use_task_prompt=use_bge_m3_task_prompt,
        )
        model.mteb_model_meta = bge_m3_model_meta(
            bge_m3,
            use_task_prompt=use_bge_m3_task_prompt,
        )
        model.mteb_model_meta.max_tokens = bge_m3_max_length
        return model

    if (
        model_arg in BGE_LARGE_EN_V1_5_ALIASES
        or "bge-large-en-v1.5" in model_arg
    ):
        model_path = (
            DEFAULT_BGE_LARGE_EN_V1_5_PATH
            if model_arg in BGE_LARGE_EN_V1_5_ALIASES
            else model_arg
        )
        bge_large_max_length = 512 if max_length is None else max_length
        logger.info(
            "Loading bge-large-en-v1.5 from %s with max_seq_length=%d, "
            "use_task_prompt=%s",
            model_path,
            bge_large_max_length,
            use_bge_large_task_prompt,
        )
        model = AOEBBGELargeEnV15Wrapper(
            model_path,
            device="cuda",
            max_seq_length=bge_large_max_length,
            torch_dtype=torch.float16,
            use_task_prompt=use_bge_large_task_prompt,
        )
        model.mteb_model_meta = bge_large_en_v1_5_model_meta(
            bge_large_en_v1_5,
            use_task_prompt=use_bge_large_task_prompt,
        )
        model.mteb_model_meta.max_tokens = bge_large_max_length
        return model

    if (
        model_arg in {"gme-2b", "gme-qwen2-vl-2b"}
        or "gme-Qwen2-VL-2B-Instruct" in model_arg
    ):
        model_path = (
            DEFAULT_GME_2B_PATH
            if model_arg in {"gme-2b", "gme-qwen2-vl-2b"}
            else model_arg
        )
        gme_max_length = 8192 if max_length is None else max_length
        logger.info(
            "Loading GME Qwen2-VL-2B from %s with max_length=%d",
            model_path,
            gme_max_length,
        )
        model = AOEBGmeQwen2VLWrapper(
            model_name="Alibaba-NLP/gme-Qwen2-VL-2B-Instruct",
            model_path=model_path,
            revision="main",
            device="cuda",
            max_length=gme_max_length,
        )
        model.mteb_model_meta = mteb.get_model_meta(
            "Alibaba-NLP/gme-Qwen2-VL-2B-Instruct"
        )
        return model
    
    if (
        model_arg in {"gme-7b", "gme-qwen2-vl-7b"}
        or "gme-Qwen2-VL-7B-Instruct" in model_arg
    ):
        model_path = (
            DEFAULT_GME_7B_PATH
            if model_arg in {"gme-7b", "gme-qwen2-vl-7b"}
            else model_arg
        )
        gme_max_length = 8192 if max_length is None else max_length
        logger.info(
            "Loading GME Qwen2-VL-7B from %s with max_length=%d",
            model_path,
            gme_max_length,
        )
        model = AOEBGmeQwen2VLWrapper(
            model_name="Alibaba-NLP/gme-Qwen2-VL-7B-Instruct",
            model_path=model_path,
            revision="main",
            device="cuda",
            max_length=gme_max_length,
        )
        model.mteb_model_meta = mteb.get_model_meta(
            "Alibaba-NLP/gme-Qwen2-VL-7B-Instruct"
        )
        return model

    raise ValueError(
        "Unsupported model. Expected 'jina-v4', 'jina-embeddings-v4', "
        "'vista', 'vista-base', 'bge-visualized-base', "
        "'mme5', 'mme5-mllama', 'mmE5-mllama-11b-instruct', "
        "'vlm2vec-lora', 'vlm2vec', 'vlm2vec-v1', 'vlm2vec2', "
        "'qwen3-vl-embedding-2b', 'qwen3-embedding-8b', 'gme-2b', "
        "'gme-qwen2-vl-2b', 'gme-7b', 'gme-qwen2-vl-7b', "
        "'nv-embed-v2', 'nvembed', 'NV-Embed-v2', "
        "'me5', 'm-e5', 'multilingual-e5-large-instruct', "
        "'intfloat/multilingual-e5-large-instruct', "
        "'e5-mistral', 'e5-mistral-7b-instruct', "
        "'intfloat/e5-mistral-7b-instruct', 'nomic', "
        "'nomic-v2-moe', 'nomic-embed-text-v2-moe', "
        "'mgte', 'm-gte', 'gte-multilingual-base', "
        "'Alibaba-NLP/gte-multilingual-base', 'bge-m3', 'BAAI/bge-m3', "
        "'bge-large-en-v1.5', 'BAAI/bge-large-en-v1.5', "
        "or a path containing 'jina-embeddings-v4', "
        "'bge-base-en-v1.5', 'mmE5-mllama-11b-instruct', 'VLM2Vec-LoRA', 'VLM2Vec-V2.0', 'Qwen3-VL-Embedding-2B', "
        "'Qwen3-Embedding-8B', 'NV-Embed-v2', 'e5-mistral-7b-instruct', "
        "'multilingual-e5-large-instruct', 'nomic-embed-text-v2-moe', "
        "'gte-multilingual-base', 'bge-m3', 'bge-large-en-v1.5' or "
        "'gme-Qwen2-VL-7B-Instruct'. "
        f"Got: {model_arg}"
    )


def get_task_registry() -> dict[str, Callable[[], object]]:
    import mteb_patch.load_data  # noqa: F401
    # from mteb_patch.tasks.browse_comp_plus import BrowseCompPlusRetrieval
    from mteb_patch.tasks.chartmimic import ChartMimicRetrieval
    from mteb_patch.tasks.design2code import Design2CodeRetrieval
    from mteb_patch.tasks.dude import DUDERetrieval
    from mteb_patch.tasks.locomo import LoCoMoRetrieval
    from mteb_patch.tasks.longmemeval import LongMemEvalRetrieval
    from mteb_patch.tasks.musique import MuSiQueRetrieval
    from mteb_patch.tasks.mvrb_composed_screenshot_retrieval import (
        MVRBComposedScreenshotRetrieval,
    )
    from mteb_patch.tasks.mvrb_screenshot_retrieval import MVRBScreenshotRetrieval
    from mteb_patch.tasks.refocus import ReFocusRetrieval
    from mteb_patch.tasks.toolret import ToolRetRetrieval
    from mteb_patch.tasks.sra_bench import SRABenchRetrieval
    from mteb.tasks.retrieval.eng import (
        BrowseCompPlusRetrieval,
        BrightRetrieval,
        TempReasonL1,
        TempReasonL2Context,
        TempReasonL2Fact,
        TempReasonL2Pure,
        TempReasonL3Context,
        TempReasonL3Fact,
        TempReasonL3Pure,

    )
    from mteb.tasks.retrieval.code import (
        FreshStackRetrieval,
        AppsRetrieval,
        CodeFeedbackMT,
        CodeFeedbackST,
        CodeTransOceanContestRetrieval,
        CodeTransOceanDLRetrieval,
        CosQARetrieval,
        StackOverflowQARetrieval,
        SyntheticText2SQLRetrieval,    
    )

    task_classes = [
        MuSiQueRetrieval,
        Design2CodeRetrieval,
        MVRBComposedScreenshotRetrieval,
        LoCoMoRetrieval,
        ToolRetRetrieval,
        MVRBScreenshotRetrieval,
        ReFocusRetrieval,
        ChartMimicRetrieval,
        LongMemEvalRetrieval,
        DUDERetrieval,
        BrowseCompPlusRetrieval,
        BrightRetrieval,
        TempReasonL1,
        TempReasonL2Context,
        TempReasonL2Fact,
        TempReasonL2Pure,
        TempReasonL3Context,
        TempReasonL3Fact,
        TempReasonL3Pure,
        SRABenchRetrieval,
        FreshStackRetrieval,
        AppsRetrieval,
        CodeFeedbackMT,
        CodeFeedbackST,
        CodeTransOceanContestRetrieval,
        CodeTransOceanDLRetrieval,
        CosQARetrieval,
        StackOverflowQARetrieval,
        SyntheticText2SQLRetrieval,    
    ]
    return {task_cls.__name__: task_cls for task_cls in task_classes}


def build_tasks(tasks_arg: str) -> list[object]:
    registry = get_task_registry()
    task_names = [name.strip() for name in tasks_arg.split(",") if name.strip()]
    if not task_names:
        raise ValueError("--tasks must contain at least one task class name.")

    unknown_task_names = [name for name in task_names if name not in registry]
    if unknown_task_names:
        supported = ", ".join(sorted(registry))
        unknown = ", ".join(unknown_task_names)
        raise ValueError(
            f"Unsupported task class name(s): {unknown}. "
            f"Supported task class names: {supported}"
        )

    return [registry[name]() for name in task_names]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local AOEB MTEB tasks for a supported multimodal model."
    )
    parser.add_argument(
        "--model",
        required=True,
        help=(
            "Model name or path. Supported names: jina-v4, jina-embeddings-v4, "
            "vista, vista-base, bge-visualized-base, "
            "mme5, mme5-mllama, mmE5-mllama-11b-instruct, "
            "vlm2vec-lora, vlm2vec-v1, vlm2vec2, qwen3-vl-embedding-2b, "
            "qwen3-embedding-8b, nv-embed-v2, nvembed, "
            "me5, m-e5, multilingual-e5-large-instruct, "
            "e5-mistral, e5-mistral-7b-instruct, "
            "nomic, nomic-v2-moe, nomic-embed-text-v2-moe, "
            "mgte, m-gte, gte-multilingual-base, "
            "bge-m3, BAAI/bge-m3, bge-large-en-v1.5, "
            "BAAI/bge-large-en-v1.5, "
            "gme-2b, gme-qwen2-vl-2b."
        ),
    )
    parser.add_argument(
        "--tasks",
        required=True,
        help="Comma-separated task class names, e.g. MuSiQueRetrieval,LoCoMoRetrieval.",
    )
    parser.add_argument("--output-dir", default="./results")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--max-length",
        type=int,
        default=None,
        help=(
            "Optional max length. The shell launcher defaults bge-large-en-v1.5, "
            "mE5, and Nomic v2 MoE to 512 and other models to 8192 unless an "
            "explicit value is provided. Jina v4 receives this through encode_kwargs."
        ),
    )
    parser.add_argument(
        "--vista-use-task-prompt",
        action="store_true",
        help="Use AOEB task prompts for VISTA. Defaults to no instruction.",
    )
    parser.add_argument(
        "--bge-m3-use-task-prompt",
        action="store_true",
        help="Use AOEB task prompts for bge-m3. Defaults to no instruction.",
    )
    parser.add_argument(
        "--bge-large-use-task-prompt",
        action="store_true",
        help="Use AOEB task prompts for bge-large-en-v1.5. Defaults to no instruction.",
    )
    parser.add_argument(
        "--nomic-use-task-prompt",
        action="store_true",
        help="Use AOEB task prompts for Nomic v2 MoE. Defaults to no instruction.",
    )
    parser.add_argument("--overwrite-strategy", default="only-missing")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks = build_tasks(args.tasks)
    model = build_model(
        args.model,
        max_length=args.max_length,
        use_vista_task_prompt=args.vista_use_task_prompt,
        use_bge_m3_task_prompt=args.bge_m3_use_task_prompt,
        use_bge_large_task_prompt=args.bge_large_use_task_prompt,
        use_nomic_task_prompt=args.nomic_use_task_prompt,
    )
    encode_kwargs = {"batch_size": args.batch_size}
    if args.max_length is not None and "jina-embeddings-v4" in args.model:
        encode_kwargs["max_length"] = args.max_length

    logger.info("Selected tasks: %s", ", ".join(t.metadata.name for t in tasks))
    logger.info("Encode kwargs: %s", encode_kwargs)
    for task in tasks:
        logger.info("Loading task data: %s", task.metadata.name)
        task.load_data()

        logger.info("Evaluating task: %s", task.metadata.name)
        mteb.evaluate(
            model,
            task,
            encode_kwargs=encode_kwargs,
            cache=ResultCache(args.output_dir),
            overwrite_strategy=args.overwrite_strategy,
        )

    logger.info("Done %d task(s).", len(tasks))


if __name__ == "__main__":
    main()

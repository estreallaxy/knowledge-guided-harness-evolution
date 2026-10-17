# from aoeb_ng.model import SentenceTransformerEmbedder, SentenceTransformerMultimodalEmbedder, st_text_length
import os

from aoeb_ng.models.jinav4 import JinaV4Wrapper
from aoeb_ng.models.vlm2vec import VLM2VecWrapper
from aoeb_ng.models.vista import vista_loader
from aoeb_ng.models.qwen3vl_embed import Qwen3VLEmbeddingWrapper
from aoeb_ng.models.gme import GmeQwen2VL
from aoeb_ng.models.mme5 import MME5


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


def get_model(model_name, device, **kwargs):
    # model = SentenceTransformerEmbedder("BAAI/bge-large-en-v1.5", device=device)
    # model.model = model.model.half()

    if model_name == 'jina-v4':
        model_path = kwargs.get('model_path', os.environ.get("AOEB_JINA_V4_PATH", "jinaai/jina-embeddings-v4"))
        model = JinaV4Wrapper(model_path)
        model.model.task = 'retrieval'

    elif model_name.startswith('gme'):
        default_model_path = os.environ.get(
            f"AOEB_GME_{model_name[-2:].upper()}_PATH",
            f"Alibaba-NLP/gme-Qwen2-VL-{model_name[-2:].upper()}-Instruct",
        )
        model_path = kwargs.get('model_path', default_model_path)
        model = GmeQwen2VL(model_path, device=device, attn_implementation='flash_attention_2')

    elif model_name == 'mme5':
        model_path = kwargs.get('model_path', os.environ.get("AOEB_MME5_PATH", "intfloat/mmE5-mllama-11b-instruct"))
        model = MME5(model_path, device=device)
            # attn_implementation='flash_attention_2'  # MllamaModel donot support flash attention yet

    elif model_name in {'vlm2vec', 'vlm2vec-lora'}:
        model_path = kwargs.get('model_path', DEFAULT_VLM2VEC_LORA_PATH)
        base_model_name = kwargs.get('base_model_name', DEFAULT_VLM2VEC_LORA_BASE_PATH)
        model = VLM2VecWrapper(model_path, base_model_name=base_model_name, device=device, max_length=8192)
        # from PIL import Image
        # img = Image.open("example.jpg").convert("RGB")
        # text = 'What is in the image'
        # query = {'text': text, 'image': img}
        # docs = ['A cat and a dog', 'A cat and a tiger']
        # query_emb = model.encode([query], batch_size=1)
        # doc_emb = model.get_text_embeddings(docs, batch_size=2)
        # score = torch.matmul(query_emb, doc_emb.transpose(0, 1))
        # print(score)  # tensor([[0.2995, 0.2051]])
        # # from model card: tensor([[0.3008, 0.2051],
        # exit()

    elif model_name == 'vista':
        from visual_bge.modeling import Visualized_BGE  # must install -e . to avoid import error?

        model_path = kwargs.get('model_path', os.environ.get("AOEB_VISTA_BASE_PATH", "BAAI/bge-base-en-v1.5"))
        model_weight = kwargs.get('model_weight', os.environ.get("AOEB_VISTA_BASE_WEIGHT_PATH", "Visualized_base_en_v1.5.pth"))
        model = vista_loader( model_path = model_path, model_weight=model_weight, image_tokens_num=196)
        # exit()

    elif model_name == 'qwen3vl-2b':
        model_path = kwargs.get('model_path', os.environ.get("AOEB_QWEN3_VL_EMBEDDING_2B_PATH", "Qwen/Qwen3-VL-Embedding-2B"))
        model = Qwen3VLEmbeddingWrapper(model_path, device=device)
        # from PIL import Image
        # queries = [
        #     "A woman playing with her dog on a beach at sunset.",
        #     "Pet owner training dog outdoors near water.",
        #     "Woman surfing on waves during a sunny day.",
        #     "City skyline view from a high-rise building at night."
        # ]
        # doc = "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust."
        # img = Image.open("demo.jpeg").convert("RGB")
        # query_emb = model.encode(queries, contains_text=True, contains_image=False, batch_size=4)
        # doc_text_emb = model.encode([doc], contains_text=True, contains_image=False, batch_size=1)
        # doc_img_emb = model.encode([img], contains_text=False, contains_image=True, batch_size=1)
        # doc_mm_emb = model.encode([{'text': doc, 'image': img}], contains_text=True, contains_image=True, batch_size=1)
        # doc_emb = torch.cat([doc_text_emb, doc_img_emb, doc_mm_emb], dim=0)
        # scores = query_emb@doc_emb.T
        # print(scores)
        # # tensor([[0.8203, 0.7227, 0.7148], [0.5234, 0.3340, 0.4395], [0.3926, 0.2871, 0.3281], [0.1104, 0.0408, 0.0703]], dtype=torch.bfloat16)
        # # from model card: [[0.81577, 0.71783, 0.717342, [0.51950, 0.33025, 0.439153, [0.38840, 0.2857, 0.3314176, [0.10926, 0.038711, 0.06952]]
        # exit()

    elif model_name == 'vlm2vec2':
        model_path = kwargs.get('model_path', DEFAULT_VLM2VEC2_PATH)
        base_model_name = kwargs.get('base_model_name', DEFAULT_VLM2VEC2_BASE_PATH)
        model = VLM2VecWrapper(model_path, base_model_name=base_model_name, device=device, max_length=8192)

        # from PIL import Image
        # img = Image.open("example.jpg").convert("RGB")
        # text = 'What is in the image'
        # query = {'text': text, 'image': img}
        # docs = ['A cat and a dog', 'A cat and a tiger']
        # query_emb = model.encode([query], batch_size=1)
        # doc_emb = model.get_text_embeddings(docs, batch_size=2)
        # score = torch.matmul(query_emb, doc_emb.transpose(0, 1))
        # print(score)  # tensor([[0.2952, 0.2346]])
        # # from model card: tensor([[0.2974, 0.2390],
    else:
        raise NotImplementedError

    return model

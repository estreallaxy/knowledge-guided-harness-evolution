from abc import ABC, abstractmethod
from enum import Enum

import torch


class InputType(str, Enum):
    query = "query"
    document = "document"


class EmbedderProtocol(ABC):
    batch_size: int = 32

    @abstractmethod
    def embed(
        self, inputs, prompt=None, input_type: InputType | None = None, task_name=None, **kwargs
    ) -> torch.Tensor:
        raise NotImplementedError

    # @abstractmethod
    # def start(self):
    #     raise NotImplementedError


class MultimodalEmbedderProtocol(EmbedderProtocol):

    def embed(
        self, inputs, task_name=None, input_type=None, **kwargs
    ) -> torch.Tensor:
        raise RuntimeError("Use embed_text, embed_image or embed_multimodal instead.")

    @abstractmethod
    def embed_text(
        self, inputs, prompt=None, input_type=None, task_name=None, **kwargs
    ) -> torch.Tensor:
        raise NotImplementedError

    @abstractmethod
    def embed_image(
        self, inputs, prompt=None, input_type=None, task_name=None, **kwargs
    ) -> torch.Tensor:
        raise NotImplementedError

    @abstractmethod
    def embed_multimodal(
        self, inputs, prompt=None, input_type=None, task_name=None, **kwargs
    ) -> torch.Tensor:
        raise NotImplementedError


class SentenceTransformerEmbedder(EmbedderProtocol):
    def __init__(self, model_path, doc_no_prompt=True, **kwargs):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_path, **kwargs)
        self.doc_no_prompt = doc_no_prompt

    def embed(self, inputs, task_name=None, input_type=None, **kwargs) -> torch.Tensor:
        texts = [i['data'] for i in inputs]
        if 'batch_size' not in kwargs:
            kwargs['batch_size'] = self.batch_size
        if self.doc_no_prompt and input_type == InputType.document:
            kwargs.pop('prompt', None)
        return self.model.encode(texts, convert_to_tensor=True, **kwargs)


class SentenceTransformerMultimodalEmbedder(MultimodalEmbedderProtocol):
    def __init__(self, model_path, doc_no_prompt=True, **kwargs):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_path, **kwargs)
        self.doc_no_prompt = doc_no_prompt

    def embed_text(
        self, inputs, task_name=None, input_type=None, **kwargs
    ) -> torch.Tensor:
        if 'batch_size' not in kwargs:
            kwargs['batch_size'] = self.batch_size
        texts = list()
        for item in inputs:
            texts.append(dict(text=item['data']))
        if self.doc_no_prompt and input_type == InputType.document:
            kwargs.pop('prompt', None)
        return self.model.encode(texts, convert_to_tensor=True, **kwargs)

    def embed_image(
        self, inputs, task_name=None, input_type=None, **kwargs
    ) -> torch.Tensor:
        if 'batch_size' not in kwargs:
            kwargs['batch_size'] = self.batch_size
        images = list()
        for item in inputs:
            images.append(dict(image=item['data']))
        if self.doc_no_prompt and input_type == InputType.document:
            kwargs.pop('prompt', None)
        return self.model.encode(images, convert_to_tensor=True, **kwargs)

    def embed_multimodal(
        self, inputs: list[dict], task_name=None, input_type=None, **kwargs
    ) -> torch.Tensor:
        from PIL.Image import Image

        if 'batch_size' not in kwargs:
            kwargs['batch_size'] = self.batch_size
        data = list()
        for item in inputs:
            ins = dict()
            text = ''
            for i in item['data']:
                if isinstance(i, str):
                    text += (i + ' ')
                elif isinstance(i, Image):
                    if 'image' not in ins:
                        ins['image'] = i
            ins['text'] = text.strip()
            data.append(ins)
        if self.doc_no_prompt and input_type == InputType.document:
            kwargs.pop('prompt', None)
        return self.model.encode(data, convert_to_tensor=True, **kwargs)


def st_text_length(text: list[int] | list[list[int]]) -> int:
    """
    Help function to get the length for the input text. Text can be either
    a list of ints (which means a single text as input), or a tuple of list of ints
    (representing several text inputs to the model).
    """
    from PIL.Image import Image

    if isinstance(text, dict):  # {key: value} case
        if 'image' in text:
            if 'text' in text:
                return len(text['text'])
            elif isinstance(text['image'], Image):
                return text['image'].size[0] * text['image'].size[1]
        return len(next(iter(text.values())))
    elif not hasattr(text, "__len__"):  # Object has no len() method
        return 1
    elif len(text) == 0 or isinstance(text[0], int):  # Empty string or list of ints
        return len(text)
    else:
        return sum([len(t) for t in text])  # Sum of length of individual strings

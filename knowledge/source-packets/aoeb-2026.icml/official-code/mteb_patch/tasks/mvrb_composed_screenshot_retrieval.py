from mteb.abstasks.retrieval import AbsTaskRetrieval
from mteb.abstasks.task_metadata import TaskMetadata


class MVRBComposedScreenshotRetrieval(AbsTaskRetrieval):
    ignore_identical_ids = False

    def dataset_transform(self, num_proc=None):
        for subset in self.hf_subsets:
            for split in self.eval_splits:
                split_data = self.dataset[subset][split]
                query_columns = [
                    column
                    for column in ("modality",)
                    if column in split_data["queries"].column_names
                ]
                corpus_columns = [
                    column
                    for column in ("text", "modality")
                    if column in split_data["corpus"].column_names
                ]
                if query_columns:
                    split_data["queries"] = split_data["queries"].remove_columns(
                        query_columns
                    )
                if corpus_columns:
                    split_data["corpus"] = split_data["corpus"].remove_columns(
                        corpus_columns
                    )

    metadata = TaskMetadata(
        name="MVRBComposedScreenshotRetrieval",
        description=(
            "MVRB Composed Screenshot Retrieval task for retrieving target "
            "screenshots from screenshot-conditioned text queries."
        ),

        reference="https://aclanthology.org/2025.acl-long.943/",

        dataset={
            "path": "vec-ai/MVRBComposedScreenshotRetrieval",
            "revision": "main",
        },
        type="Retrieval",
        category="it2i",
        modalities=["text", "image"],
        eval_splits=["test"],
        eval_langs={
            "knowledge_relation": ["eng-Latn"],
            "news_to_wiki": ["eng-Latn"],
            "product_discovery": ["eng-Latn"],
            "wiki_to_product": ["eng-Latn"],
        },
        main_score="ndcg_at_10",
        date=("2025-02-17", "2025-07-01"),
        domains=["Web", "News", "Academic", "E-commerce", "Programming", "Written"],
        task_subtypes=["Image Text Retrieval"],
        license="mit",
        annotations_creators="human-annotated",
        dialect=[],
        sample_creation="created",
        bibtex_citation=r"""
@inproceedings{liu-etal-2025-information,
  title = "Any Information Is Just Worth One Single Screenshot: Unifying Search With Visualized Information Retrieval",
  author = "Liu, Zheng and Liu, Ze and Liang, Zhengyang and Zhou, Junjie and Xiao, Shitao and Gao, Chao and Zhang, Chen Jason and Lian, Defu",
  booktitle = "Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
  month = jul,
  year = "2025",
  address = "Vienna, Austria",
  publisher = "Association for Computational Linguistics",
  url = "https://aclanthology.org/2025.acl-long.943/",
  doi = "10.18653/v1/2025.acl-long.943",
  pages = "19238--19261",
}
""",
        prompt={
            "query": "Provide a specific description of the image along with the following question.",
            # vd prompt
            "document": "Understand the content of the provided document image.",
            # img prompt
            # "document": "Understand the content of the provided image.",
        },
    )

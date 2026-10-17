from mteb.abstasks.retrieval import AbsTaskRetrieval
from mteb.abstasks.task_metadata import TaskMetadata


class MVRBScreenshotRetrieval(AbsTaskRetrieval):
    ignore_identical_ids = False

    metadata = TaskMetadata(
        name="MVRBScreenshotRetrieval",
        description=(
            "MVRB Screenshot Retrieval task for retrieving relevant screenshot "
            "images from text queries across product, paper, repository, news, "
            "chart, document, and slide subsets."
        ),

        reference="https://aclanthology.org/2025.acl-long.943/",

        dataset={
            "path": "vec-ai/MVRBScreenshotRetrieval",
            "revision": "main",
        },
        type="Retrieval",
        category="t2i",
        modalities=["text", "image"],
        eval_splits=["test"],
        eval_langs={
            "chart_retrieval": ["eng-Latn"],
            "doc_retrieval": ["eng-Latn"],
            "news_retrieval": ["eng-Latn"],
            "paper_retrieval": ["eng-Latn"],
            "product_retrieval": ["eng-Latn"],
            "repo_retrieval": ["eng-Latn"],
            "slide_retrieval": ["eng-Latn"],
        },
        main_score="ndcg_at_10",
        date=("2025-02-17", "2025-07-01"),
        domains=["Web", "News", "Academic", "E-commerce", "Programming", "Written"],
        task_subtypes=["Image Text Retrieval"],
        license="mit",
        annotations_creators="automatic",
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
            "query": "Retrieve the screenshot image that contains the answer to the question.",
            # vd prompt
            "document": "Understand the content of the provided document image.",
            # img prompt
            # "document": "Understand the content of the provided image.",
        },
    )

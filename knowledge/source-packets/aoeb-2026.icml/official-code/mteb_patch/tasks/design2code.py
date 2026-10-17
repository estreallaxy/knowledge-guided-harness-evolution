from mteb.abstasks.retrieval import AbsTaskRetrieval
from mteb.abstasks.task_metadata import TaskMetadata


class Design2CodeRetrieval(AbsTaskRetrieval):
    ignore_identical_ids = False

    def dataset_transform(self, num_proc=None):
        for subset in self.hf_subsets:
            for split in self.eval_splits:
                split_data = self.dataset[subset][split]
                query_columns = [
                    column
                    for column in ("image", "modality")
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
        name="Design2CodeRetrieval",
        description=(
            "Design2Code retrieval task matching front-end code or webpage "
            "design descriptions to rendered webpage screenshot images."
        ),

        reference="https://arxiv.org/abs/2403.03163",

        dataset={
            "path": "vec-ai/Design2Code",
            "revision": "main",
        },
        type="Retrieval",
        category="t2i",
        modalities=["text", "image"],
        eval_splits=["test"],
        eval_langs=["eng-Latn"],
        main_score="ndcg_at_10",
        date=("2024-03-05", "2025-02-09"),
        domains=["Programming", "Web", "Written"],
        task_subtypes=["Code retrieval", "Image Text Retrieval"],
        license="odc-by",
        annotations_creators="human-annotated",
        dialect=[],
        sample_creation="found",
        bibtex_citation=r"""
@article{si2024design2code,
  title={Design2Code: Benchmarking Multimodal Code Generation for Automated Front-End Engineering},
  author={Si, Chenglei and Zhang, Yanzhe and Li, Ryan and Yang, Zhengyuan and Liu, Ruibo and Yang, Diyi},
  journal={arXiv preprint arXiv:2403.03163},
  year={2024},
}
""",
        prompt={
            "query": "Based on the provided front-end code (HTML/CSS), retrieve the matching visual UI design image rendered by this code.Query:",
            # "document": "Understand the content of the provided image.",
        },
    )

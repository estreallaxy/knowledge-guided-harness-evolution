from mteb.abstasks.retrieval import AbsTaskRetrieval
from mteb.abstasks.task_metadata import TaskMetadata


class DUDERetrieval(AbsTaskRetrieval):
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
        name="DUDERetrieval",
        description=(
            "DUDE document understanding retrieval task for finding relevant "
            "visually rich document pages for document QA queries."
        ),

        reference="https://arxiv.org/abs/2305.08455",

        dataset={
            "path": "vec-ai/DUDE",
            "revision": "main",
        },
        type="Retrieval",
        category="t2i",
        modalities=["text", "image"],
        eval_splits=["test"],
        eval_langs=["eng-Latn"],
        main_score="ndcg_at_10",
        date=("2023-05-15", "2023-09-11"),
        domains=["Written", "Non-fiction"],
        task_subtypes=["Question answering", "Image Text Retrieval"],
        license="not specified",
        annotations_creators="human-annotated",
        dialect=[],
        sample_creation="found",
        bibtex_citation=r"""
@article{vanlandeghem2023document,
  title={Document Understanding Dataset and Evaluation (DUDE)},
  author={Van Landeghem, Jordy and Tito, Ruben and Borchmann, Lukasz and Pietruszka, Michal and Joziak, Pawel and Powalski, Rafal and Jurkiewicz, Dawid and Coustaty, Mickael and Ackaert, Bertrand and Valveny, Ernest and Blaschko, Matthew and Moens, Sien and Stanislawek, Tomasz},
  journal={arXiv preprint arXiv:2305.08455},
  year={2023},
}
""",
        prompt={
            "query": "",
            # "document": "Understand the content of the provided image.",
        },
    )

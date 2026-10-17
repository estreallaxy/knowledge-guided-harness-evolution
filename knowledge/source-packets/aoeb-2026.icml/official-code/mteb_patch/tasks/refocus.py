from mteb.abstasks.retrieval import AbsTaskRetrieval
from mteb.abstasks.task_metadata import TaskMetadata


class ReFocusRetrieval(AbsTaskRetrieval):
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
                    for column in ("image", "modality")
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
        name="ReFocusRetrieval",
        description=(
            "ReFocus multimodal retrieval task for retrieving visual-editing "
            "Python snippets or visual thoughts for structured image "
            "understanding questions."
        ),

        reference="https://arxiv.org/abs/2501.05452",

        dataset={
            "path": "vec-ai/ReFocus",
            "revision": "main",
        },
        type="Retrieval",
        category="it2t",
        modalities=["text", "image"],
        eval_splits=["test"],
        eval_langs=["eng-Latn"],
        main_score="ndcg_at_10",
        date=("2025-01-09", "2025-01-09"),
        domains=["Academic", "Written"],
        task_subtypes=["Code retrieval", "Image Text Retrieval"],
        license="apache-2.0",
        annotations_creators="LM-generated and reviewed",
        dialect=[],
        sample_creation="LM-generated and verified",
        bibtex_citation=r"""
@article{fu2025refocus,
  title={ReFocus: Visual Editing as a Chain of Thought for Structured Image Understanding},
  author={Fu, Zeyi and Li, Shicheng and Lyu, Qing and Zhang, Cheng and Shen, Yue and Yang, Zhe and Liu, Yang and Xie, Xing},
  journal={arXiv preprint arXiv:2501.05452},
  year={2025},
}
""",
        prompt={
            "query": "Given a chart image and a question about it, retrieve the Python code snippet that focuses or highlights the chart element, category, axis value, or data series needed to answer the question.",
        },
    )

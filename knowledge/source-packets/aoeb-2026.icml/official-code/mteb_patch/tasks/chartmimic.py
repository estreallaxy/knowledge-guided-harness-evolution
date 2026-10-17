from mteb.abstasks.retrieval import AbsTaskRetrieval
from mteb.abstasks.task_metadata import TaskMetadata


class ChartMimicRetrieval(AbsTaskRetrieval):
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
        name="ChartMimicRetrieval",
        description=(
            "ChartMimic multimodal retrieval task pairing chart-generation "
            "instructions or code with corresponding chart images."
        ),

        reference="https://arxiv.org/abs/2406.09961",

        dataset={
            "path": "vec-ai/ChartMimic",
            "revision": "main",
        },
        type="Retrieval",
        category="t2i",
        modalities=["text", "image"],
        eval_splits=["test"],
        eval_langs=["eng-Latn"],
        main_score="ndcg_at_10",
        date=("2024-06-14", "2025-02-28"),
        domains=["Academic", "Written"],
        task_subtypes=["Code retrieval", "Image Text Retrieval"],
        license="cc-by-4.0",
        annotations_creators="human-annotated",
        dialect=[],
        sample_creation="found",
        bibtex_citation=r"""
@article{yang2024chartmimic,
  title={ChartMimic: Evaluating LMM's Cross-Modal Reasoning Capability via Chart-to-Code Generation},
  author={Yang, Cheng and Shi, Chufan and Liu, Yaxin and Shui, Bo and Wang, Junjie and Jing, Mohan and Xu, Linran and Zhu, Xinyu and Li, Siheng and Zhang, Yuxiang and Liu, Gongye and Nie, Xiaomei and Cai, Deng and Yang, Yujiu},
  journal={arXiv preprint arXiv:2406.09961},
  year={2024},
}
""",
        prompt={    
            "query": ""
        }
    )

from mteb.abstasks.retrieval import AbsTaskRetrieval
from mteb.abstasks.task_metadata import TaskMetadata


class MuSiQueRetrieval(AbsTaskRetrieval):
    ignore_identical_ids = True

    metadata = TaskMetadata(
        name="MuSiQueRetrieval",
        description=(
            "Multi-hop QA retrieval task derived from MuSiQue-Ans, requiring "
            "retrieval of supporting passages for connected reasoning."
        ),
        reference="https://arxiv.org/abs/2108.00573",
        dataset={
            "path": "vec-ai/MuSiQue",
            "revision": "main",
        },
        type="Retrieval",
        category="t2t",
        modalities=["text"],
        eval_splits=["test"],
        eval_langs=["eng-Latn"],
        main_score="ndcg_at_10",
        date=("2021-08-02", "2022-05-05"),
        domains=["Encyclopaedic", "Written"],
        task_subtypes=["Question answering", "Reasoning as Retrieval"],
        license="cc-by-sa-4.0",
        annotations_creators="human-annotated",
        dialect=[],
        sample_creation="found",
        bibtex_citation=r"""
@article{trivedi2022musique,
  title={MuSiQue: Multihop Questions via Single-hop Question Composition},
  author={Trivedi, Harsh and Balasubramanian, Niranjan and Khot, Tushar and Sabharwal, Ashish},
  journal={Transactions of the Association for Computational Linguistics},
  volume={10},
  pages={539--554},
  year={2022},
  publisher={MIT Press},
}
""",
        prompt={"query": "Given a multi-hop question, retrieve all supporting passages that enable connected reasoning to answer the question."},
    )

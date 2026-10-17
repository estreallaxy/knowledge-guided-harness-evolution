from mteb.abstasks.retrieval import AbsTaskRetrieval
from mteb.abstasks.task_metadata import TaskMetadata


class SRABenchRetrieval(AbsTaskRetrieval):
    ignore_identical_ids = True

    metadata = TaskMetadata(
        name="SRABenchRetrieval",
        description=(
            "SRA-Bench skill retrieval task for retrieving reusable skills "
            "needed by agentic AI systems."
        ),

        reference="https://arxiv.org/abs/2604.24594",

        dataset={
            "path": "vec-ai/SRA",
            "revision": "main",
        },
        type="Retrieval",
        category="t2t",
        modalities=["text"],
        eval_splits=["test"],
        eval_langs={
            "brief": ["eng-Latn"],
            "full": ["eng-Latn"],
        },
        main_score="ndcg_at_10",
        date=("2026-04-28", "2026-04-28"),
        domains=["Academic", "Programming", "Medical", "Web", "Written"],
        task_subtypes=["Article retrieval", "Code retrieval"],
        license="mit",
        annotations_creators="human-annotated",
        dialect=[],
        sample_creation="created",
        bibtex_citation=r"""
@article{su2026skill,
  title={Skill Retrieval Augmentation for Agentic AI},
  author={Su, Weihang and Long, Jianming and Ai, Qingyao and Tang, Yichen and Wang, Changyue and Tu, Yiteng and Liu, Yiqun},
  journal={arXiv preprint arXiv:2604.24594},
  year={2026},
}
""",
        prompt={
            "query": "Given a problem or task, retrieve the most relevant skill documents needed to solve it."
        },
    )

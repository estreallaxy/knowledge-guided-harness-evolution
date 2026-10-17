from mteb.abstasks.task_metadata import TaskMetadata

from mteb_patch.abstasks.memory_retrieval import MemoryRetrieval


class LongMemEvalRetrieval(MemoryRetrieval):
    ignore_identical_ids = True

    metadata = TaskMetadata(
        name="LongMemEvalRetrieval",
        description=(
            "LongMemEval-M memory retrieval task for retrieving user-side "
            "utterances that support long-term interactive memory questions."
        ),

        reference="https://arxiv.org/abs/2410.10813",

        dataset={
            "path": "vec-ai/LongMemEvalM",
            "revision": "main",
        },
        type="Retrieval",
        category="t2t",
        modalities=["text"],
        eval_splits=["test"],
        eval_langs=["eng-Latn"],
        main_score="ndcg_at_10",
        date=("2024-10-14", "2025-03-04"),
        domains=["Social", "Written"],
        task_subtypes=["Conversational retrieval", "Question answering"],
        license="mit",
        annotations_creators="LM-generated and reviewed",
        dialect=[],
        sample_creation="LM-generated and verified",
        bibtex_citation=r"""
@article{wu2024longmemeval,
  title={LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory},
  author={Wu, Di and Wang, Hongwei and Yu, Wenhao and Zhang, Yuwei and Chang, Kai-Wei and Yu, Dong},
  journal={arXiv preprint arXiv:2410.10813},
  year={2024},
}
""",
        prompt={"query": "Given a query requiring long-term memory retrieval, retrieve the precise segments from a massive corpus that store the target information."},
    )

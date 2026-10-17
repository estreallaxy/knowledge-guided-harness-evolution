from mteb.abstasks.task_metadata import TaskMetadata

from mteb_patch.abstasks.memory_retrieval import MemoryRetrieval


class LoCoMoRetrieval(MemoryRetrieval):
    ignore_identical_ids = True

    metadata = TaskMetadata(
        name="LoCoMoRetrieval",
        description=(
            "LoCoMo memory retrieval task over very long multi-session "
            "conversations, with single-hop, multi-hop, temporal, "
            "open-domain, and adversarial subsets."
        ),

        reference="https://arxiv.org/abs/2402.17753",

        dataset={
            "path": "vec-ai/LoCoMo",
            "revision": "main",
        },
        type="Retrieval",
        category="t2t",
        modalities=["text"],
        eval_splits=["test"],
        eval_langs={
            "adversarial": ["eng-Latn"],
            "multi-hop-retrieval": ["eng-Latn"],
            "open-domain-knowledge": ["eng-Latn"],
            "single-hop-retrieval": ["eng-Latn"],
            "temporal-reasoning": ["eng-Latn"],
        },
        main_score="ndcg_at_10",
        date=("2024-02-27", "2024-02-27"),
        domains=["Social", "Written"],
        task_subtypes=["Conversational retrieval", "Question answering"],
        license="cc-by-nc-4.0",
        annotations_creators="LM-generated and reviewed",
        dialect=[],
        sample_creation="LM-generated and verified",
        bibtex_citation=r"""
@article{maharana2024evaluating,
  title={Evaluating Very Long-Term Conversational Memory of LLM Agents},
  author={Maharana, Adyasha and Lee, Dong-Ho and Tulyakov, Sergey and Bansal, Mohit and Barbieri, Francesco and Fang, Yuwei},
  journal={arXiv preprint arXiv:2402.17753},
  year={2024},
}
""",
        prompt={"query": "Given a query about a long-term conversation, retrieve the specific dialogue segments from the extensive history that are most relevant for answering the question or supporting event summarization. Ensure the retrieved content maintains contextual coherence."},
    )

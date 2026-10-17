from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path
from time import time
from typing import Any

import datasets
from mteb._evaluators import RetrievalEvaluator
from mteb._evaluators.retrieval_metrics import make_score_dict
from mteb.abstasks.retrieval import (
    AbsTaskRetrieval,
    _filter_queries_without_positives,
)
from mteb.abstasks.retrieval_dataset_loaders import RetrievalSplitData
from mteb.models import (
    CrossEncoderProtocol,
    EncoderProtocol,
    MTEBModels,
    SearchCrossEncoderWrapper,
    SearchEncoderWrapper,
    SearchProtocol,
)
from mteb.types import EncodeKwargs, RetrievalOutputType, ScoresDict


logger = logging.getLogger(__name__)

CANDIDATE_FEATURES = datasets.Features(
    {
        "query_id": datasets.Value("string"),
        "candidate_doc_ids": datasets.Sequence(datasets.Value("string")),
    }
)


class MemoryRetrieval(AbsTaskRetrieval):
    """Retrieval task wrapper for per-query candidate pools.

    The model still searches the full corpus. The resulting scores are filtered
    to each query's candidate pool before metrics are computed.
    """

    memory_candidates: dict[tuple[str, str], dict[str, list[str]]]

    def load_data(self, num_proc: int | None = None, **kwargs) -> None:
        if self.data_loaded and hasattr(self, "memory_candidates"):
            return

        if not self.data_loaded:
            super().load_data(num_proc=num_proc, **kwargs)

        self.memory_candidates = {}
        hf_subsets = (
            list(self.dataset.keys())
            if self.hf_subsets is None
            else list(self.hf_subsets)
        )

        for hf_subset in hf_subsets:
            for split in self.eval_splits:
                candidates = self._load_candidate_pool(
                    hf_subset=hf_subset,
                    split=split,
                    num_proc=num_proc,
                )
                data_split = self.dataset[hf_subset][split]
                self._validate_candidate_pool(
                    candidates,
                    data_split["relevant_docs"],
                    hf_subset=hf_subset,
                    hf_split=split,
                )
                self.memory_candidates[(hf_subset, split)] = candidates

    def _load_candidate_pool(
        self,
        *,
        hf_subset: str,
        split: str,
        num_proc: int | None,
    ) -> dict[str, list[str]]:
        dataset_path = self.metadata.dataset["path"]
        revision = self.metadata.dataset["revision"]
        trust_remote_code = self.metadata.dataset.get("trust_remote_code", False)
        config = f"{hf_subset}-candidates" if hf_subset != "default" else "candidates"

        dataset_kwargs: dict[str, Any] = {}
        if not Path(dataset_path).exists():
            dataset_kwargs["trust_remote_code"] = trust_remote_code
            dataset_kwargs["revision"] = revision

        split_name = self._resolve_candidate_split(
            dataset_path=dataset_path,
            config=config,
            split=split,
            dataset_kwargs=dataset_kwargs,
        )
        candidate_ds = datasets.load_dataset(
            dataset_path,
            config,
            split=split_name,
            num_proc=num_proc,
            **dataset_kwargs,
        )
        candidate_ds = candidate_ds.cast(CANDIDATE_FEATURES).select_columns(
            ["query_id", "candidate_doc_ids"]
        )

        candidate_map: dict[str, list[str]] = {}
        for row in candidate_ds:
            query_id = row["query_id"]
            if query_id in candidate_map:
                raise ValueError(
                    f"duplicate candidate pool for query_id={query_id!r} "
                    f"({hf_subset=}, {split=})"
                )
            candidate_map[query_id] = list(row["candidate_doc_ids"])

        logger.info(
            "Loaded %d candidate pools for %s/%s.",
            len(candidate_map),
            hf_subset,
            split,
        )
        return candidate_map

    @staticmethod
    def _resolve_candidate_split(
        *,
        dataset_path: str,
        config: str,
        split: str,
        dataset_kwargs: Mapping[str, Any],
    ) -> str:
        try:
            split_names = datasets.get_dataset_split_names(
                dataset_path,
                config_name=config,
                **dataset_kwargs,
            )
        except Exception as exc:
            raise ValueError(f"failed to load candidate config: {config}") from exc

        if split in split_names:
            return split
        if len(split_names) == 1:
            return split_names[0]
        raise ValueError(
            f"split {split!r} not found in candidate config {config!r}: {split_names}"
        )

    @staticmethod
    def _validate_candidate_pool(
        candidate_map: Mapping[str, list[str]],
        relevant_docs: Mapping[str, Mapping[str, int]],
        *,
        hf_subset: str,
        hf_split: str,
    ) -> None:
        for query_id, docs in relevant_docs.items():
            if query_id not in candidate_map:
                raise ValueError(
                    f"missing candidate pool for query_id={query_id!r} "
                    f"({hf_subset=}, {hf_split=})"
                )

            candidate_doc_ids = set(candidate_map[query_id])
            if not candidate_doc_ids:
                raise ValueError(
                    f"empty candidate pool for query_id={query_id!r} "
                    f"({hf_subset=}, {hf_split=})"
                )

            missing_positive_doc_ids = [
                doc_id
                for doc_id, score in docs.items()
                if int(score) > 0 and doc_id not in candidate_doc_ids
            ]
            if missing_positive_doc_ids:
                preview = ", ".join(missing_positive_doc_ids[:5])
                raise ValueError(
                    f"positive qrels missing from candidate pool for "
                    f"query_id={query_id!r} ({hf_subset=}, {hf_split=}): {preview}"
                )

    @staticmethod
    def _filter_results_by_candidates(
        results: RetrievalOutputType,
        candidate_map: Mapping[str, list[str]],
    ) -> RetrievalOutputType:
        filtered_results: RetrievalOutputType = {}

        for query_id, doc_scores in results.items():
            if query_id not in candidate_map:
                raise ValueError(f"missing candidate pool for query_id={query_id!r}")

            candidate_doc_ids = set(candidate_map[query_id])
            filtered_doc_scores = {
                doc_id: score
                for doc_id, score in doc_scores.items()
                if doc_id in candidate_doc_ids
            }
            if not filtered_doc_scores:
                raise ValueError(
                    f"query_id={query_id!r} has no results after candidate filtering"
                )
            filtered_results[query_id] = filtered_doc_scores

        return filtered_results

    def _evaluate_subset(
        self,
        model: MTEBModels,
        data_split: RetrievalSplitData,
        encode_kwargs: EncodeKwargs,
        hf_split: str,
        hf_subset: str,
        prediction_folder: Path | None = None,
        num_proc: int | None = None,
        **kwargs,
    ) -> ScoresDict:
        data_split["relevant_docs"], data_split["queries"] = (
            _filter_queries_without_positives(
                data_split["relevant_docs"], data_split["queries"]
            )
        )
        candidate_map = self.memory_candidates[(hf_subset, hf_split)]
        self._validate_candidate_pool(
            candidate_map,
            data_split["relevant_docs"],
            hf_subset=hf_subset,
            hf_split=hf_split,
        )

        retriever = RetrievalEvaluator(
            corpus=data_split["corpus"],
            queries=data_split["queries"],
            task_metadata=self.metadata,
            hf_split=hf_split,
            hf_subset=hf_subset,
            top_ranked=data_split["top_ranked"],
            top_k=len(data_split["corpus"]),
            **kwargs,
        )

        search_model: SearchProtocol
        if isinstance(model, EncoderProtocol) and not isinstance(model, SearchProtocol):
            search_model = SearchEncoderWrapper(model)
        elif isinstance(model, CrossEncoderProtocol):
            search_model = SearchCrossEncoderWrapper(model)
        elif isinstance(model, SearchProtocol):
            search_model = model
        else:
            raise TypeError(
                f"RetrievalEvaluator expects a SearchInterface, Encoder, or CrossEncoder, got {type(model)}"
            )

        start_time = time()
        results = retriever(
            search_model,
            encode_kwargs=encode_kwargs,
            num_proc=num_proc,
        )
        end_time = time()
        logger.debug(
            "Running memory retrieval task - Time taken to retrieve: %.2f seconds",
            end_time - start_time,
        )

        filtered_results = self._filter_results_by_candidates(results, candidate_map)

        if prediction_folder:
            self._save_task_predictions(
                filtered_results,
                model,
                prediction_folder,
                hf_subset=hf_subset,
                hf_split=hf_split,
            )

        logger.info("Running memory retrieval task - Evaluating retrieval scores...")
        (
            all_scores,
            ndcg,
            _map,
            recall,
            precision,
            naucs,
            mrr,
            naucs_mrr,
            hit_rate,
        ) = retriever.evaluate(
            data_split["relevant_docs"],
            filtered_results,
            self.k_values,
            ignore_identical_ids=self.ignore_identical_ids,
            skip_first_result=self.skip_first_result,
        )
        task_specific_scores = self.task_specific_scores(
            all_scores,
            data_split["relevant_docs"],
            filtered_results,
            hf_split=hf_split,
            hf_subset=hf_subset,
        )
        logger.info("Running memory retrieval task - Finished.")
        return make_score_dict(
            ndcg,
            _map,
            recall,
            precision,
            mrr,
            naucs,
            naucs_mrr,
            hit_rate,
            task_specific_scores,
            self._previous_results_model_meta,
        )

from typing import List, Dict, Callable

import config.rules
import json


class Rule:
    def __init__(self, predicate: Callable[[Dict], bool], ignore: List[str]):
        self.predicate = predicate
        self.ignore = ignore

    def applies(self, c: Dict) -> bool:
        """
        Applies the rule to the given configuration.

        :param c: The configuration to check.
        :return: True if the rule applies, False otherwise.
        """
        try:
            return self.predicate(c)
        except Exception:
            return False

    def apply(self, c: Dict) -> Dict:
        """
        Applies the rule to the given configuration and returns a new configuration
        with the ignored keys removed.

        :param c: The configuration to apply the rule to.
        :return: A new configuration with the ignored keys removed.
        """
        return {k: v for k, v in c.items() if k not in self.ignore}


def make_hashable(config: dict) -> str:
    # Convert nested dicts to consistent, sorted JSON string
    def normalize(val):
        if isinstance(val, dict):
            return {k: normalize(v) for k, v in sorted(val.items())}
        elif isinstance(val, list):
            return [normalize(v) for v in val]
        else:
            return val

    normalized = {k: normalize(v) for k, v in sorted(config.items())}
    return json.dumps(normalized, sort_keys=True)


class RuleBasedHyperparameterValidator:
    def __init__(self, model: str):
        self.rules = config.rules.MODEL_HYPERPARAMETERS_RULES.get(model, [])

    def filter_configs(self, configs: list[dict]) -> list[dict]:
        seen = set()
        results = []

        for c in configs:
            filtered_config = c.copy()

            for rule in self.rules:
                if rule.applies(filtered_config):
                    filtered_config = rule.apply(filtered_config)

            # python dictionaries are not hashable
            key = make_hashable(filtered_config)
            if key not in seen:
                seen.add(key)
                results.append(c)

        return results

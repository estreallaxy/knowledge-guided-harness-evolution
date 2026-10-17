from typing import Callable, List, Dict


class Rule:
    def __init__(self, predicate: Callable[[Dict], bool], ignore: List[str]):
        self.predicate = predicate
        self.ignore = ignore

    def applies(self, config: Dict) -> bool:
        try:
            return any(self.predicate(config[k]) for k in config.keys())
        except Exception:
            return False

    def apply(self, config: Dict) -> Dict:
        filtered_config = config.copy()
        for k, v in filtered_config.items():
            if k in self.ignore:
                del filtered_config[k]
            elif isinstance(v, dict):
                if self.predicate(filtered_config[k]):
                    for ignore_key in self.ignore:
                        if ignore_key in filtered_config[k]:
                            del filtered_config[k][ignore_key]

        return filtered_config

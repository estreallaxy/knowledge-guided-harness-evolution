# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/a2a_llm/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/config.template.toml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/green_agent/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/kustomization.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-adservice.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-cartservice.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-checkoutservice.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-currencyservice.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-deny-all.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-emailservice.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-frontend.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-loadgenerator.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-paymentservice.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-productcatalogservice.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-recommendationservice.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/app-k8s/microservices-demo/kustomize/components/network-policies/network-policy-redis.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/app-k8s/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/app-k8s/run_workflow.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/app-malt/eval_with_sem_err.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/app-malt/eval_with_spider.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/app-malt/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/app-malt/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/app-route/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.

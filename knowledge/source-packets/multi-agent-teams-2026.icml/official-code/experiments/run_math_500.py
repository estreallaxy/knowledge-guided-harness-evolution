"""Launch script for MATH-500 collaborative experiments."""

import os
import random
import statistics
from datetime import datetime
from typing import List, Optional
import time

import hydra
import wandb
from datasets import load_dataset
from dotenv import load_dotenv
from omegaconf import DictConfig, OmegaConf
from pydantic import BaseModel, Field

from teamwork.backend_utils import (
    build_backend_summary,
    create_backend_from_config,
    get_api_key,
    get_model_name_from_backend,
    sanitize_model_name_for_summary,
)
from teamwork.agent import TeamAgent
from teamwork.profiles import AgentProfile
from teamwork.tasks.math_500_problem_task import Math500ProblemTask

# Load environment variables
load_dotenv()


def get_unique_ids_from_run(run_name: str, project: str = "math-500-teamwork", entity: Optional[str] = None) -> List[str]:
    """Retrieve unique_ids from a W&B run's history.
    
    Args:
        run_name: Name of the W&B run to retrieve unique_ids from
        project: W&B project name
        entity: W&B entity/team name (optional)
        
    Returns:
        List of unique_ids (as strings) from the run
    """
    api = wandb.Api()
    
    # Search for the run by name (not by ID/path)
    print(f"Searching for run with name: '{run_name}' in project '{project}' (entity: {entity or 'default'})...")
    
    # Construct project path for searching
    if entity:
        project_path = f"{entity}/{project}"
    else:
        project_path = project
        # Try to detect entity from wandb settings
        try:
            settings = wandb.Settings()
            if hasattr(settings, 'entity') and settings.entity:
                detected_entity = settings.entity
                project_path = f"{detected_entity}/{project}"
                print(f"Using detected entity: {detected_entity}")
        except Exception:
            pass
    
    try:
        # Get all runs from the project
        all_runs = api.runs(project_path)
        
        # Find run with matching name
        matching_run = None
        for r in all_runs:
            if r.name == run_name:
                matching_run = r
                break
        
        if matching_run is None:
            # Try partial match or show similar runs
            similar_runs = []
            for r in all_runs:
                if run_name in r.name or r.name.startswith(run_name[:50]) or run_name[:50] in r.name:
                    similar_runs.append(r)
            
            error_msg = f"Could not find run with name '{run_name}' in project '{project_path}'"
            if similar_runs:
                error_msg += f"\nFound {len(similar_runs)} runs with similar names:"
                for r in similar_runs[:5]:
                    error_msg += f"\n  - {r.name} (ID: {r.id})"
            else:
                error_msg += f"\nNo runs found with similar names. Total runs in project: {len(list(all_runs))}"
            raise ValueError(error_msg)
        
        run = matching_run
        print(f"Found run: {run.name} (ID: {run.id})")
        
        # Get full history (all logged steps)
        history = run.history()
        
        if 'unique_id' not in history.columns:
            raise ValueError(f"Run {run_name} does not contain 'unique_id' in history")
        
        # Extract unique IDs and convert to strings
        unique_ids = history['unique_id'].dropna().unique().tolist()
        unique_ids = [str(uid).strip() for uid in unique_ids if str(uid).strip()]
        
        print(f"Found {len(unique_ids)} unique unique_ids in reference run")
        return sorted(unique_ids)
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to search for run '{run_name}' in project '{project_path}': {e}")

# Set longer timeout for W&B operations
os.environ['WANDB_INIT_TIMEOUT'] = '600'
os.environ['WANDB_HTTP_TIMEOUT'] = '600'


class BackendConfig(BaseModel):
    """Configuration for a single backend."""
    provider: str = Field(description="Backend provider (openai, anthropic, gemini)")
    model: Optional[str] = Field(default=None, description="Model name")
    temperature: Optional[float] = Field(default=None, description="Sampling temperature")


class AgentBackendConfig(BaseModel):
    """Configuration for agents using a specific backend."""
    provider: str = Field(description="Backend provider (openai, anthropic, gemini)")
    count: int = Field(ge=1, description="Number of agents using this backend")
    model: Optional[str] = Field(default=None, description="Model name")
    temperature: Optional[float] = Field(default=None, description="Sampling temperature")


class Math500Config(BaseModel):
    """Configuration for MATH-500 experiment."""
    
    dataset_name: str = Field(default="HuggingFaceH4/MATH-500", description="Dataset name")
    limit: Optional[int] = Field(default=None, description="Limit number of problems (for testing)")
    reference_run_name: Optional[str] = Field(default=None, description="W&B run name to retrieve unique_ids from (filters dataset to same subset)")
    
    max_rounds: int = Field(ge=1, description="Maximum collaboration rounds")
    
    def model_post_init(self, __context) -> None:
        """Validate configuration after initialization."""
        # Ensure only one of limit or reference_run_name is specified
        if self.limit is not None and self.reference_run_name is not None:
            raise ValueError(
                "Cannot specify both 'limit' and 'reference_run_name'. "
                "Use 'limit' for random sampling or 'reference_run_name' to filter by unique_ids from a reference run."
            )
    num_agents: Optional[int] = Field(default=None, ge=1, description="Number of agents (single backend mode)")
    
    decision_mode: str = Field(default="expert_not_mentioned", description="Decision strategy")
    most_capable_model_name: Optional[str] = Field(default=None, description="Fallback expert model name")
    
    # LLM Fallback for Answer Equivalence
    use_llm_fallback: bool = Field(default=True, description="Use LLM as final fallback for equivalence checking")
    llm_fallback_model: str = Field(default="gpt-5", description="Model name for LLM fallback (e.g., 'gpt-4o', 'gpt-5')")
    llm_fallback_api_key: Optional[str] = Field(default=None, description="API key for LLM fallback (defaults to OPENAI_API_KEY)")
    
    seed: int = Field(default=42, description="Random seed")
    
    # Backends
    backend: Optional[BackendConfig] = Field(default=None, description="Single backend config")
    agent_backends: Optional[List[AgentBackendConfig]] = Field(default=None, description="Mixed backend configs")
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key (for gemini provider)")
    
    # W&B
    wandb_project: str = Field(default="math-500-teamwork", description="W&B project name")
    wandb_entity: Optional[str] = Field(default=None, description="W&B entity/team name")
    wandb_group: Optional[str] = Field(default=None, description="W&B group name")
    wandb_tags: Optional[List[str]] = Field(default=None, description="W&B tags")

    def generate_run_name(self, total_agents: int, backend_summary: str, num_problems: int) -> str:
        """Generate unique experiment run name."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        decision_str = f"_{self.decision_mode}" if self.decision_mode != "expert_not_mentioned" else ""
        seed_str = f"_s{self.seed}" if self.seed is not None else ""
        problems_str = f"p{num_problems}"
        return f"math500_{problems_str}_n{total_agents}_r{self.max_rounds}{decision_str}_{backend_summary}{seed_str}_{timestamp}"


@hydra.main(version_base=None, config_path="configs", config_name="math_500")
def main(cfg: DictConfig) -> None:
    """Run MATH-500 experiment."""
    config = Math500Config(**cfg)

    # 1. Initialize Agents
    agents: List[TeamAgent] = []
    agent_counter = 0
    backend_summary = ""
    
    if config.agent_backends:
        # Mixed backend mode
        print("Running in MIXED BACKEND mode")
        
        for backend_cfg in config.agent_backends:
            provider = backend_cfg.provider
            count = backend_cfg.count
            
            api_key = get_api_key(config, provider)
            
            for _ in range(count):
                agent_seed = config.seed + agent_counter
                backend = create_backend_from_config(
                    backend_cfg=backend_cfg,
                    api_key=api_key,
                    seed=agent_seed
                )
                model_name = get_model_name_from_backend(backend, provider)
                agent_name = f"Agent-{agent_counter}-{provider}-{model_name}"
                
                agents.append(TeamAgent(
                    profile=AgentProfile(
                        agent_id=agent_counter,
                        name=agent_name,
                        role="Mathematician",
                        system_prompt="You are a helpful mathematician working in a team to solve math problems. You will first come up with your own solution, present it to your team members, and then work together to reach a final solution.",
                        metadata={"backend_provider": provider, "backend_model": model_name}
                    ),
                    backend=backend
                ))
                agent_counter += 1
        
        total_agents = agent_counter
        backend_summary = build_backend_summary(config.agent_backends)
        
    elif config.backend and config.num_agents:
        # Single backend mode
        print("Running in SINGLE BACKEND mode")
        provider = config.backend.provider
        
        api_key = get_api_key(config, provider)
        
        model_name = ""
        for agent_id in range(config.num_agents):
            agent_seed = config.seed + agent_id
            backend = create_backend_from_config(
                backend_cfg=config.backend,
                api_key=api_key,
                seed=agent_seed
            )
            agent_model_name = get_model_name_from_backend(backend, provider)
            if agent_id == 0:
                model_name = agent_model_name
            
            agent_name = f"Agent-{agent_id}-{provider}-{agent_model_name}"
            
            agents.append(TeamAgent(
                profile=AgentProfile(
                    agent_id=agent_id,
                    name=agent_name,
                    role="Mathematician",
                    system_prompt="You are a helpful mathematician working in a team to solve math problems. You will first come up with your own solution, present it to your team members, and then work together to reach a final solution.",
                    metadata={"backend_provider": provider, "backend_model": agent_model_name}
                ),
                backend=backend
            ))
        
        total_agents = config.num_agents
        if model_name:
            sanitized_model = sanitize_model_name_for_summary(model_name)
            backend_summary = f"{provider}_{sanitized_model}"
        else:
            backend_summary = provider
        
    else:
        raise ValueError("Invalid configuration: must specify backend+num_agents or agent_backends")

    # 2. Validate Fallback Model
    if config.decision_mode == "reveal_expert" and config.most_capable_model_name:
        found = False
        for agent in agents:
            if config.most_capable_model_name in agent.profile.metadata.get("backend_model", ""):
                found = True
                break
        if not found:
            print(f"WARNING: configured most_capable_model_name '{config.most_capable_model_name}' not found in any agent backend.")

    # 3. Determine Number of Problems (for run name)
    # Use limit if specified, otherwise assume full dataset (500 problems)
    num_problems = config.limit if config.limit is not None else 500
    
    # 4. Initialize W&B (with number of problems in run name)
    run_name = config.generate_run_name(total_agents, backend_summary, num_problems)
    wandb_config = OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    
    run = wandb.init(
        project=config.wandb_project,
        entity=config.wandb_entity,
        name=run_name,
        group=config.wandb_group,
        tags=config.wandb_tags,
        config=wandb_config
    )
    
    print(f"Experiment: {run_name}")
    print(f"Dataset: {config.dataset_name}")
    print(f"Agents: {total_agents} | Rounds: {config.max_rounds}")
    
    # 5. Load Dataset
    print("Loading dataset...")
    dataset = load_dataset(config.dataset_name, split="test")
    total_problems_available = len(dataset)
    
    # Filter by unique_ids from reference run if specified
    if config.reference_run_name:
        print(f"Filtering dataset using unique_ids from reference run: {config.reference_run_name}")
        reference_unique_ids = get_unique_ids_from_run(
            config.reference_run_name,
            project=config.wandb_project,
            entity=config.wandb_entity
        )
        
        # Convert to set for faster lookup
        reference_unique_ids_set = set(reference_unique_ids)
        
        # Find indices where unique_id matches reference unique_ids
        filtered_indices = []
        for idx, example in enumerate(dataset):
            example_unique_id = example.get('unique_id', None)
            if example_unique_id is not None:
                if str(example_unique_id).strip() in reference_unique_ids_set:
                    filtered_indices.append(idx)
        
        dataset = dataset.select(filtered_indices)
        print(f"Filtered to {len(dataset)} problems matching reference run (from {total_problems_available} total)")
        
        if len(dataset) == 0:
            raise ValueError(f"No problems found matching unique_ids from reference run '{config.reference_run_name}'")
        
        if len(dataset) != len(reference_unique_ids):
            print(f"WARNING: Found {len(dataset)} matching problems but reference run had {len(reference_unique_ids)} unique_ids")
            print("Some unique_ids from reference run may not exist in current dataset")
    
    elif config.limit:
        # Randomly sample problems when limit is specified
        rng = random.Random(config.seed)
        indices = list(range(total_problems_available))
        rng.shuffle(indices)
        selected_indices = sorted(indices[:config.limit])  # Sort for reproducibility
        dataset = dataset.select(selected_indices)
        print(f"Randomly selected {len(dataset)} problems from {total_problems_available} total")
    else:
        print(f"Running on entire dataset: {total_problems_available} problems")
    
    print(f"Loaded {len(dataset)} problems")
    
    # 6. Execution Loop
    # Track aggregate metrics
    agent_correct_counts = {agent.profile.agent_id: 0 for agent in agents}
    team_correct_count = 0
    total_problems = 0
    run_id = run.id  # Store run ID for artifact naming
    
    for i, problem_data in enumerate(dataset):
        print(f"\nProblem {i+1}/{len(dataset)}")
        
        # Use a unique ID from dataset or index
        # MATH-500 usually doesn't have 'id' column, so use index if needed or check columns
        # HuggingFaceH4/MATH-500 has columns: problem, solution, subject, level, unique_id
        unique_id = problem_data.get('unique_id', i)
        
        # Initialize Task
        # Seed should be global seed + problem index for reproducibility and uniqueness per problem
        task_seed = config.seed + i
        
        task = Math500ProblemTask(
            agent_ids=[a.profile.agent_id for a in agents],
            max_rounds=config.max_rounds,
            problem_data=problem_data,
            unique_id=unique_id,
            seed=task_seed,
            decision_mode=config.decision_mode,
            most_capable_model_name=config.most_capable_model_name,
            use_llm_fallback=config.use_llm_fallback,
            llm_fallback_model=config.llm_fallback_model,
            llm_fallback_api_key=config.llm_fallback_api_key or config.openai_api_key,
        )
        
        # Execute
        result = task.execute(agents)
        
        # Update aggregate counters
        total_problems += 1
        if result.score == 1.0:  # team_score of 1.0 means correct
            team_correct_count += 1
            
        for aid, correct in result.metadata["individual_correctness"].items():
            if correct:
                agent_correct_counts[aid] += 1
        
        # Log Granular Data (per-problem data - each wandb.log() call creates a new row in history)
        log_data = {
            "problem_index": i,
            "unique_id": str(unique_id),
            "ground_truth": result.metadata["ground_truth"],
            # "team_solution": result.metadata["team_solution"],  # Full solution text - commented out to reduce log size
            "team_answer": result.metadata["team_answer"],  # Extracted answer
            "team_score": result.score,  # 1.0 = correct, 0.0 = incorrect
        }
        
        # Individual Data (per agent, per problem - these are logged as separate columns per row)
        for aid in result.metadata["individual_answers"]:
            # log_data[f"agent_{aid}_solution"] = result.metadata["individual_solutions"][aid]  # Full solution text - commented out to reduce log size
            log_data[f"agent_{aid}_answer"] = result.metadata["individual_answers"][aid]  # Extracted answer
            log_data[f"agent_{aid}_correctness"] = int(result.metadata["individual_correctness"][aid])
            
        # Voting Data (per problem - these change per problem)
        if result.metadata.get("declared_best_agent_id") is not None:
            log_data["declared_best_agent_id"] = result.metadata["declared_best_agent_id"]
        if result.metadata.get("coordinator_agent_id") is not None:
            log_data["coordinator_agent_id"] = result.metadata["coordinator_agent_id"]
        if result.metadata.get("revealed_expert_agent_id") is not None:
            log_data["revealed_expert_agent_id"] = result.metadata["revealed_expert_agent_id"]
            
        # Log this problem's data as a new row in W&B history
        # Use problem index as step to ensure each problem gets its own row
        wandb.log(log_data, step=i)
        
        # Print team result with individual agent performance
        team_correct = (result.score == 1.0)
        ground_truth = result.metadata["ground_truth"]
        team_answer = result.metadata["team_answer"]  # Use extracted answer, not full solution
        
        print(f"Result: Team Correct={team_correct}")
        print(f"  Ground Truth: {ground_truth}")
        print(f"  Team Answer: {team_answer}")
        print("  Individual Agent Performance:")
        for agent in agents:
            agent_id = agent.profile.agent_id
            model_name = agent.profile.metadata.get("backend_model", "unknown")
            individual_answer = result.metadata["individual_answers"].get(agent_id, "N/A")  # Use extracted answer
            individual_correct = result.metadata["individual_correctness"].get(agent_id, False)
            print(f"    Agent {agent_id} ({model_name}): {individual_answer} {'✓ Correct' if individual_correct else '✗ Incorrect'}")
        
        # Log trajectories as artifact before clearing
        # Use problem index in artifact name to distinguish between problems
        artifact = wandb.Artifact(f"trajectories-problem-{i}-{run_id}", type="trajectories")  # type: ignore
        for agent in agents:
            agent_id = agent.profile.agent_id
            model_name = agent.profile.metadata.get("backend_model", "unknown")
            
            # Use backend's own prompt formatting logic to get full representation
            # This includes system prompt + all trajectory turns as the agent sees them
            full_prompt = agent.backend.format_full_prompt(
                agent_profile=agent.profile,
                trajectory=agent.trajectory
            )
            
            # Add header with agent info and problem info
            agent_transcript = f"=== Problem {i} (ID: {unique_id}) ===\n=== Agent {agent_id} ({model_name}) ===\n\n{full_prompt}"
            
            # Add trajectory as text file to artifact
            with artifact.new_file(f"agent_{agent_id}_trajectory.txt", mode="w") as f:
                f.write(agent_transcript)
        
        wandb.log_artifact(artifact)
        
        # Reset agent trajectories for next problem
        # Important: Clear memory so previous problem context doesn't leak
        for agent in agents:
            agent.trajectory.clear()

        # Sleep every 25 problems for 5 minutes
        if i % 25 == 0 and i > 0:
            print("Sleeping for 5 minutes every 25 problems...")
            time.sleep(300)

    # 6. Compute and Log Aggregate Metrics
    dataset_team_accuracy = team_correct_count / total_problems if total_problems > 0 else 0
    dataset_agent_accuracies = {
        aid: count / total_problems for aid, count in agent_correct_counts.items()
    }
    
    if dataset_agent_accuracies:
        dataset_avg_individual_accuracy = statistics.mean(dataset_agent_accuracies.values())
        dataset_best_individual_accuracy = max(dataset_agent_accuracies.values())
    else:
        dataset_avg_individual_accuracy = 0
        dataset_best_individual_accuracy = 0
        
    team_improvement_over_avg = dataset_team_accuracy - dataset_avg_individual_accuracy
    team_improvement_over_best = dataset_team_accuracy - dataset_best_individual_accuracy
    
    # Log Summary
    wandb.run.summary["dataset_team_accuracy"] = dataset_team_accuracy
    wandb.run.summary["dataset_avg_individual_accuracy"] = dataset_avg_individual_accuracy
    wandb.run.summary["dataset_best_individual_accuracy"] = dataset_best_individual_accuracy
    wandb.run.summary["team_improvement_over_avg"] = team_improvement_over_avg
    wandb.run.summary["team_improvement_over_best"] = team_improvement_over_best
    
    for aid, acc in dataset_agent_accuracies.items():
        wandb.run.summary[f"agent_{aid}_accuracy"] = acc
    
    # Remove per-problem metrics from summary (W&B automatically adds last value of all logged metrics)
    # We only want aggregate metrics in summary, not per-problem data
    per_problem_metrics_to_remove = [
        "problem_index", "unique_id", "ground_truth", "team_answer", "team_score",
        "declared_best_agent_id", "coordinator_agent_id", "revealed_expert_agent_id"
    ]
    # Also remove all agent-specific per-problem metrics
    for aid in agent_correct_counts.keys():
        per_problem_metrics_to_remove.extend([
            f"agent_{aid}_answer",
            f"agent_{aid}_correctness"
        ])
    
    # Use get() method to safely check and remove metrics
    # wandb.run.summary doesn't support 'in' operator, so use get() instead
    for metric in per_problem_metrics_to_remove:
        if wandb.run.summary.get(metric) is not None:
            try:
                del wandb.run.summary[metric]
            except (KeyError, AttributeError):
                # Metric doesn't exist or can't be deleted, skip it
                pass

    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Team Accuracy: {dataset_team_accuracy:.2%}")
    print(f"Avg Individual Accuracy: {dataset_avg_individual_accuracy:.2%}")
    print(f"Best Individual Accuracy: {dataset_best_individual_accuracy:.2%}")
    print(f"Improvement over Avg: {team_improvement_over_avg:+.2%}")
    print(f"Improvement over Best: {team_improvement_over_best:+.2%}")
    
    wandb.finish()


if __name__ == "__main__":
    main()


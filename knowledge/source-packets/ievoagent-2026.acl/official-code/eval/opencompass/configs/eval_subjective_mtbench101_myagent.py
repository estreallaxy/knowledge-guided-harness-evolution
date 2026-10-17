from mmengine.config import read_base

with read_base():
    from .datasets.subjective.multiround.mtbench101_judge import subjective_datasets

from opencompass.models import HuggingFaceCausalLM, HuggingFace, HuggingFaceChatGLM3, OpenAI, Gemini,VLLM
from opencompass.models.customAgent import MyCustomModel
from opencompass.partitioners import NaivePartitioner, SizePartitioner
from opencompass.partitioners.sub_naive import SubjectiveNaivePartitioner
from opencompass.partitioners.sub_size import SubjectiveSizePartitioner
from opencompass.runners import LocalRunner
from opencompass.runners import SlurmSequentialRunner
from opencompass.tasks import OpenICLInferTask
from opencompass.tasks.subjective_eval import SubjectiveEvalTask
from opencompass.summarizers import MTBench101Summarizer

# ---------------------------------------------------------------------------------------------------------

api_meta_template = dict(
    round=[
        dict(role='SYSTEM', api_role='SYSTEM'),
        dict(role='HUMAN', api_role='HUMAN'),
        dict(role='BOT', api_role='BOT', generate=True),
    ]
)
_meta_template = dict(
    round=[
        dict(role='HUMAN', api_role='user'),
        dict(role='BOT', api_role='assistant'),
    ],
)

models = [
    dict(
        type=MyCustomModel, 
        abbr='myagent',
        path='', 
        generation_kwargs=dict(),
        meta_template=_meta_template,
        max_out_len=4096,
        max_seq_len=4096,
        batch_size=8,
        run_cfg=dict(num_gpus=1, num_procs=1),
    )
]

datasets = [*subjective_datasets]


# 修改建议：暂时改为本地运行，排除 Slurm 环境干扰
infer = dict(
    partitioner=dict(type=SizePartitioner, max_task_size=10000),
    runner=dict(
        type=LocalRunner,
        max_num_workers=4, 
        task=dict(type=OpenICLInferTask),
    ),
)



judge_models = [dict(
    abbr='openai-gpt-4o',
    type=OpenAI,
    path='gpt-4o', 
    key='YOUR_API_KEY',
    meta_template=api_meta_template,
    query_per_second=8,
    max_out_len=4096,
    max_seq_len=4096,
    batch_size=8,
    temperature=0.8,
)]

eval = dict(
    partitioner=dict(type=SubjectiveSizePartitioner, max_task_size=100000, mode='singlescore', models=models, judge_models=judge_models),
    runner=dict(type=LocalRunner, max_num_workers=32, task=dict(type=SubjectiveEvalTask)),
)

summarizer = dict(type=MTBench101Summarizer, judge_type='single')

work_dir = 'outputs/mtbench101/'

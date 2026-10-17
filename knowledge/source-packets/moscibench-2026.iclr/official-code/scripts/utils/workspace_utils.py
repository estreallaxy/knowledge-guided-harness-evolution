import os
import re  
import shutil
from scripts.logs import logger


def update_imports_in_file(file_path: str, old_module: str, new_module: str, baseline_name: str):
    """
    更新单个Python文件中的import语句
    
    Args:
        file_path: Python文件路径
        old_module: 旧的模块名 (如 'MLE')
        new_module: 新的模块名 (如 'aerial_cactus_identification')
        baseline_name: baseline名称 (如 'MLE', 'Custom_Baseline')
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern1 = rf'import\s+workspace\.{old_module}\.workflows'
        replacement1 = f'import workspace.{baseline_name}.{new_module}.workflows'
        content = re.sub(pattern1, replacement1, content)
        
 .
        pattern2 = rf'from\s+workspace\.{old_module}\.workflows'
        replacement2 = f'from workspace.{baseline_name}.{new_module}.workflows'
        content = re.sub(pattern2, replacement2, content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True
    except Exception as e:
        logger.error(f"Error updating {file_path}: {e}")
        return False


def update_all_imports(directory: str, old_module: str, new_module: str, baseline_name: str):
    """
    递归更新目录中所有Python文件的import语句
    
    Args:
        directory: 要处理的目录路径
        old_module: 旧的模块名 (如 'MLE')
        new_module: 新的模块名 (如 'aerial_cactus_identification')
        baseline_name: baseline名称 (如 'MLE', 'Custom_Baseline')
    """
    updated_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path, old_module, new_module, baseline_name):
                    updated_files.append(file_path)
                    logger.info(f"Updated imports in: {file_path}")
    
    return updated_files


def setup_baseline_workflow_directories(dataset: str, optimized_path: str, initial_round_path: str, baseline_name: str):
    """
    Setup workflow directories for baseline evaluation
    Copy agent and template directories from agents/{baseline_name}/workflows to workspace/{baseline_name}/{dataset}/workflows
    Only overwrite agent and template directories, preserve other directories like round_* results
    
    Args:
        dataset: Dataset name (e.g., 'aerial-cactus-identification')
        optimized_path: Root path for storing results (e.g., 'workspace')
        initial_round_path: Directory containing baseline workflows (e.g., 'agents')
        baseline_name: Name of the baseline to use (e.g., 'ReAct', 'Custom_Baseline')
    """
    # Normalize dataset name (replace hyphens with underscores)
    dataset_normalized = dataset.replace('-', '_')
    
    # Define paths
    optimized_workflows_path = os.path.join(optimized_path, baseline_name, dataset_normalized, "workflows")
    initial_workflows_path = os.path.join(initial_round_path, baseline_name, "workflows")
    
    # Create workflows directory if it doesn't exist
    os.makedirs(optimized_workflows_path, exist_ok=True)
    
    # Check if source workflows exist
    if not os.path.exists(initial_workflows_path):
        raise FileNotFoundError(f"Baseline workflows not found: {initial_workflows_path}")
    
    # Copy or update agent and template directories
    source_dirs = ['agent', 'template']  # Only these two directories
    
    for dir_name in source_dirs:
        src_dir = os.path.join(initial_workflows_path, dir_name)
        dst_dir = os.path.join(optimized_workflows_path, dir_name)
        
        if os.path.exists(src_dir):
            # Remove existing directory if it exists (only agent/template)
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
                logger.info(f"Removed existing {dir_name} directory: {dst_dir}")
            
            # Copy the directory
            shutil.copytree(src_dir, dst_dir)
            logger.info(f"Copied {dir_name} directory from {src_dir} to {dst_dir}")
        else:
            logger.warning(f"Source directory not found: {src_dir}")
    
    # Update imports in the copied directories
    logger.info(f"Updating imports from 'workspace.MLE.workflows' to 'workspace.{baseline_name}.{dataset_normalized}.workflows'...")
    updated_files = update_all_imports(optimized_workflows_path, "MLE", dataset_normalized, baseline_name)
    logger.info(f"Successfully updated {len(updated_files)} files")
    
    logger.info(f"Baseline workflow setup completed. Preserved existing result directories in: {optimized_workflows_path}")


def list_workflow_directories(optimized_path: str, baseline_name: str, dataset: str):
    """
    列出workflow目录中的所有子目录
    
    Args:
        optimized_path: 根路径
        baseline_name: baseline名称
        dataset: 数据集名称
    
    Returns:
        目录列表
    """
    dataset_normalized = dataset.replace('-', '_')
    workflows_path = os.path.join(optimized_path, baseline_name, dataset_normalized, "workflows")
    
    if not os.path.exists(workflows_path):
        return []
    
    try:
        directories = [d for d in os.listdir(workflows_path) 
                      if os.path.isdir(os.path.join(workflows_path, d))]
        return sorted(directories)
    except Exception as e:
        logger.error(f"Error listing directories in {workflows_path}: {e}")
        return []


def clean_old_result_directories(optimized_path: str, baseline_name: str, dataset: str, keep_latest: int = 5):
    """
    清理旧的结果目录，只保留最新的几个
    
    Args:
        optimized_path: 根路径
        baseline_name: baseline名称
        dataset: 数据集名称
        keep_latest: 保留最新的目录数量
    """
    dataset_normalized = dataset.replace('-', '_')
    workflows_path = os.path.join(optimized_path, baseline_name, dataset_normalized, "workflows")
    
    if not os.path.exists(workflows_path):
        return
    
    try:
        # 获取所有round_开头的目录
        result_dirs = [d for d in os.listdir(workflows_path) 
                      if d.startswith('round_') and os.path.isdir(os.path.join(workflows_path, d))]
        
        if len(result_dirs) <= keep_latest:
            logger.info(f"Only {len(result_dirs)} result directories found, no cleanup needed")
            return
        
        # 按修改时间排序，保留最新的
        result_dirs_with_time = []
        for dir_name in result_dirs:
            dir_path = os.path.join(workflows_path, dir_name)
            mtime = os.path.getmtime(dir_path)
            result_dirs_with_time.append((dir_name, mtime))
        
        # 按时间排序，保留最新的keep_latest个
        result_dirs_with_time.sort(key=lambda x: x[1], reverse=True)
        dirs_to_remove = result_dirs_with_time[keep_latest:]
        
        for dir_name, _ in dirs_to_remove:
            dir_path = os.path.join(workflows_path, dir_name)
            shutil.rmtree(dir_path)
            logger.info(f"Removed old result directory: {dir_path}")
        
        logger.info(f"Cleaned up {len(dirs_to_remove)} old result directories, kept latest {keep_latest}")
        
    except Exception as e:
        logger.error(f"Error cleaning old directories: {e}")


def get_workflow_structure(optimized_path: str, baseline_name: str, dataset: str):
    """
    获取workflow目录结构信息
    
    Args:
        optimized_path: 根路径
        baseline_name: baseline名称
        dataset: 数据集名称
    
    Returns:
        目录结构字典
    """
    dataset_normalized = dataset.replace('-', '_')
    workflows_path = os.path.join(optimized_path, baseline_name, dataset_normalized, "workflows")
    
    structure = {
        'workflows_path': workflows_path,
        'exists': os.path.exists(workflows_path),
        'source_dirs': [],
        'result_dirs': [],
        'other_dirs': []
    }
    
    if not structure['exists']:
        return structure
    
    try:
        for item in os.listdir(workflows_path):
            item_path = os.path.join(workflows_path, item)
            if os.path.isdir(item_path):
                if item in ['agent', 'template']:
                    structure['source_dirs'].append(item)
                elif item.startswith('round_'):
                    structure['result_dirs'].append(item)
                else:
                    structure['other_dirs'].append(item)
        
        # 排序
        structure['source_dirs'].sort()
        structure['result_dirs'].sort()
        structure['other_dirs'].sort()
        
    except Exception as e:
        logger.error(f"Error getting workflow structure: {e}")
    
    return structure
import asyncio
import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, DefaultDict,Callable
import pandas as pd
import zipfile
import tarfile
import io
from collections import Counter, defaultdict
from datetime import datetime

from scripts.formatter import BaseFormatter, FormatError, XmlFormatter, CodeFormatter, TextFormatter
from scripts.async_llm import AsyncLLM
from scripts.logs import logger

from workspace.MLE.workflows.template.operator_an import *
from workspace.MLE.workflows.template.op_prompt import *
import re


import json
import nbformat


# --- Optimized Helper and Constants ---

MAX_FILES_TO_SUMMARIZE = 10
MAX_FILES_IN_LIST = 50  # Maximum number of files to include in file_list_str
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
COMPRESSED_EXTENSIONS = {'.zip', '.tar', '.gz', '.tgz', '.tar.gz', '.tar.bz2', '.tbz2'}

def _create_file_summary(filepath: Path, n_rows=5) -> str:
    """
    Creates a comprehensive summary of a file's content based on its type.
    Enhanced to handle .xyz files specifically for materials science data.
    """
    if not filepath or not filepath.exists() or not filepath.is_file():
        return f"[File not found or is not a file: {filepath}]"

    try:
        file_size_kb = os.path.getsize(filepath) / 1024
        suffix = filepath.suffix.lower()

        if suffix in IMAGE_EXTENSIONS:
            return f"[Image file: {filepath.name} ({file_size_kb:.1f} KB)]"
        
        if suffix in COMPRESSED_EXTENSIONS:
            return f"[Compressed file: {filepath.name} ({file_size_kb:.1f} KB)]"

        # 特殊处理 .xyz 文件（分子/晶体结构文件）
        if suffix == '.xyz':
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [f.readline().strip() for _ in range(20)]  # 读取前20行
                
                # 解析 xyz 文件结构
                atom_count = 0
                lattice_vectors = []
                atoms_info = []
                
                for line in lines:
                    if not line:
                        continue
                    if line.startswith('lattice_vector'):
                        lattice_vectors.append(line)
                    elif line.startswith('#') or line.startswith('lattice_vector'):
                        continue
                    else:
                        # 尝试解析原子信息行
                        parts = line.split()
                        if len(parts) >= 4:  # 原子符号 + x, y, z 坐标
                            atoms_info.append(line)
                            atom_count += 1
                        if atom_count >= 5:  # 只显示前5个原子
                            break
                
                summary_parts = [
                    f"--- Summary for {filepath.name} ({file_size_kb:.1f} KB) ---",
                    f"Format: XYZ (Crystal/Molecular Structure)",
                ]
                
                if lattice_vectors:
                    summary_parts.append(f"Lattice vectors: {len(lattice_vectors)}")
                    summary_parts.extend(lattice_vectors[:3])  # 显示前3个晶格向量
                
                if atoms_info:
                    summary_parts.append(f"Sample atoms (showing first {min(len(atoms_info), 5)}):")
                    summary_parts.extend(atoms_info[:5])
                
                return "\n".join(summary_parts)
                
            except Exception as e:
                return f"[Error reading XYZ file {filepath.name}: {e}]"

        if suffix == '.csv':
            df_head = pd.read_csv(filepath, nrows=n_rows, low_memory=False)
            head_str = df_head.to_string()
            return (
                f"--- Summary for {filepath.name} ({file_size_kb:.1f} KB) ---\n"
                f"File Head:\n{head_str}\n\n"
            )
        
        if suffix == '.parquet':
            try:
                import pyarrow.parquet as pq
            except ImportError:
                return f"[Cannot read Parquet file: {filepath.name}. 'pyarrow' is not installed.]"
            
            pf = pq.ParquetFile(filepath)
            schema_str = str(pf.schema)
            num_rows = pf.metadata.num_rows
            df_sample = next(pf.iter_batches(batch_size=5)).to_pandas()

            return (
                f"--- Summary for {filepath.name} ({file_size_kb:.1f} KB) ---\n"
                f"Format: Parquet\n"
                f"Total Rows: {num_rows}\n"
                f"Schema:\n{schema_str}\n\n"
                f"Sample Data (first 5 rows):\n{df_sample.to_string()}"
            )

        # Default to text file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [next(f).strip() for _ in range(n_rows * 2)]
            content_peek = "\n".join(lines)
            return (
                f"--- Summary for {filepath.name} ({file_size_kb:.1f} KB) ---\n"
                f"Content Head:\n{content_peek}"
            )

    except pd.errors.EmptyDataError:
        return f"[File is empty: {filepath.name}]"
    except Exception as e:
        return f"[Error reading file {filepath.name}: {type(e).__name__} {e}]"


class Operator:
    def __init__(self, llm: Optional[AsyncLLM], name: str):
        self.name = name
        self.llm = llm

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def _fill_node(self, op_class, prompt, mode=None, **extra_kwargs):
        if not self.llm:
            raise RuntimeError(f"LLM not initialized for operator {self.name}")
        formatter = self._create_formatter(op_class, mode)
        try:
            if formatter:
                # For XML, call_with_format returns a dict matching the model
                # For Code/Text, it returns a string
                response = await self.llm.call_with_format(prompt, formatter, **extra_kwargs)
            else:
                # Fallback
                response = await self.llm(prompt)
            
            # Standardize output: XML returns dict, others return {"response": string}
            if isinstance(response, dict):
                # XML formatter already returns the dict {field: value}
                # CodeFormatter via call_with_format returns {'python_code': code} if model has that field
                return response
            else:
                # TextFormatter or raw call returns string, wrap it.
                # Also handle CodeFormatter if not using a model with specific field name
                key = "response"
                if mode == "code_fill" and hasattr(op_class, 'python_code'):
                    key = "python_code"
                return {key: response}

        except FormatError as e:
            logger.error(f"Format error in {self.name}: {str(e)}")
            # Fallback: try raw call and simple extraction? For now, just return error.
            return {"error": f"FormatError: {e}"}
        except Exception as e:
            logger.error(f"LLM call error in {self.name}: {type(e).__name__} - {e}\n{traceback.format_exc()}")
            return {"error": f"LLMError: {e}"}


    def _create_formatter(self, op_class, mode=None) -> Optional[BaseFormatter]:
        """Create appropriate formatter based on operation class and mode"""
        if mode == "xml_fill":
            return XmlFormatter.from_model(op_class)
        elif mode == "code_fill":
            # Pass model to CodeFormatter so call_with_format can return dict {'python_code': code}
            return CodeFormatter(pydantic_model=op_class) 
        elif mode == "single_fill":
            return TextFormatter()
        return None

# ================= Operators =================

class Custom(Operator):
    def __init__(self, llm: AsyncLLM, name: str = "Custom"):
        super().__init__(llm, name)

    async def __call__(self, input, instruction):
        prompt = instruction + input
        # Returns {"response": "..."}
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        return response

# --- OPTIMIZED ANALYSIS OPERATOR ---

class Analysis(Operator):
    def __init__(self, llm: AsyncLLM, name: str = "Analysis"):
        super().__init__(llm, name)
        # 减少参数，聚焦核心功能
        self.MAX_SAMPLE_FILES = 5      # 每个目录最多展示的文件数
        self.MAX_CONTENT_SUMMARIES = 10 # 最多生成的内容摘要数

    def _generate_data_description(self, data_path: Path) -> str:
            """Generate comprehensive data directory summary with samples from all important data files"""
            import json
            import os
            from pathlib import Path
            from collections import Counter, defaultdict
            import random
            
            if not data_path.exists() or not data_path.is_dir():
                return f"[Data directory not found: {data_path}]"
            
            # Performance configuration
            MAX_DEPTH = 4
            MAX_FILES_PER_DIR = 100
            MAX_DIRS_PER_LEVEL = 20
            MAX_CONTENT_SAMPLES_PER_TYPE = 5  # Per file type, not total
            MAX_IMAGE_EXAMPLES = 5
            MAX_CSV_ROWS = 5
            MAX_COLUMNS_DISPLAY = 10
            MAX_COLUMN_NAME_LENGTH = 20
            MAX_CELL_LENGTH = 15
            MAX_TOTAL_LINE_LENGTH = 150
            NUMERIC_DIR_SAMPLES = 2
            
            # Enhanced file type categories including bioinformatics formats
            DATA_EXTENSIONS = {'.csv', '.json', '.parquet', '.xlsx', '.xls', '.txt', '.tsv', '.h5', '.hdf5'}
            BIOINFORMATICS_EXTENSIONS = {'.bed', '.fam', '.bim', '.vcf', '.vcf.gz', '.fastq', '.fq', '.fasta', '.fa', 
                                        '.sam', '.bam', '.gtf', '.gff', '.ped', '.map'}
            IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.tif'}
            CODE_EXTENSIONS = {'.py', '.ipynb', '.r', '.sql', '.sh'}
            DOC_EXTENSIONS = {'.md', '.rst', '.pdf', '.docx'}
            MODEL_EXTENSIONS = {'.pkl', '.pickle', '.h5', '.pth', '.pt', '.onnx', '.joblib'}
            CONFIG_EXTENSIONS = {'.yaml', '.yml', '.toml', '.ini', '.cfg'}
            STRUCTURE_EXTENSIONS = {'.xyz', '.pdb', '.mol', '.sdf'}
            
            lines = []
            content_samples_per_type = defaultdict(int)  # Track samples per file type
            
            def format_number(n):
                """Format large numbers concisely"""
                if n >= 1000000:
                    return f"{n/1000000:.1f}M"
                elif n >= 1000:
                    return f"{n/1000:.1f}K"
                return str(n)
            
            def truncate_string(s, max_length):
                """Truncate string with ellipsis if too long"""
                s = str(s)
                if len(s) <= max_length:
                    return s
                return s[:max_length-3] + "..."
            
            def format_column_list(columns, max_display=8):
                """Format column list with smart truncation"""
                if len(columns) <= max_display:
                    col_names = [truncate_string(c, MAX_COLUMN_NAME_LENGTH) for c in columns]
                    return f"Columns ({len(columns)}): {', '.join(col_names)}"
                else:
                    keep_each = max_display // 2
                    first_cols = [truncate_string(c, MAX_COLUMN_NAME_LENGTH) for c in columns[:keep_each]]
                    last_cols = [truncate_string(c, MAX_COLUMN_NAME_LENGTH) for c in columns[-keep_each:]]
                    return f"Columns ({len(columns)}): {', '.join(first_cols)} ... {', '.join(last_cols)}"
            
            def get_file_category(ext):
                """Categorize file by extension with enhanced bioinformatics support"""
                ext = ext.lower()
                if ext in DATA_EXTENSIONS:
                    return "data"
                elif ext in BIOINFORMATICS_EXTENSIONS:
                    return "bioinformatics"
                elif ext in IMAGE_EXTENSIONS:
                    return "image"
                elif ext in CODE_EXTENSIONS:
                    return "code"
                elif ext in DOC_EXTENSIONS:
                    return "doc"
                elif ext in MODEL_EXTENSIONS:
                    return "model"
                elif ext in CONFIG_EXTENSIONS:
                    return "config"
                elif ext in STRUCTURE_EXTENSIONS:
                    return "structure"
                else:
                    return "other"
            
            def read_tabular_sample(file_path, max_rows=MAX_CSV_ROWS):
                """Read CSV/TSV file with smart truncation and delimiter detection"""
                try:
                    # Determine delimiter based on file extension
                    file_ext = file_path.suffix.lower()
                    delimiter = '\t' if file_ext == '.tsv' else ','
                    
                    # Try pandas first
                    try:
                        import pandas as pd
                        
                        df = pd.read_csv(file_path, nrows=max_rows + 1, delimiter=delimiter)
                        
                        result = []
                        file_type = "TSV" if file_ext == '.tsv' else "CSV"
                        result.append(f"{file_type} Shape: ({df.shape[0]} rows, {df.shape[1]} cols)")
                        result.append(format_column_list(df.columns.tolist()))
                        
                        # Handle wide tables
                        if len(df.columns) > MAX_COLUMNS_DISPLAY:
                            keep_cols = MAX_COLUMNS_DISPLAY // 2
                            display_cols = list(df.columns[:keep_cols]) + list(df.columns[-keep_cols:])
                            df_display = df[display_cols].copy()
                            df_display.insert(keep_cols, '...', '...')
                        else:
                            df_display = df.copy()
                        
                        # Truncate cell values
                        for col in df_display.columns:
                            if col != '...':
                                df_display[col] = df_display[col].apply(lambda x: truncate_string(x, MAX_CELL_LENGTH))
                        
                        result.append("\nFirst rows:")
                        for idx, row in df_display.head(max_rows).iterrows():
                            row_str = ' | '.join([truncate_string(str(v), MAX_CELL_LENGTH) for v in row.values])
                            if len(row_str) > MAX_TOTAL_LINE_LENGTH:
                                row_str = row_str[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                            result.append(f"  {row_str}")
                        
                        # Check total rows
                        try:
                            total_rows = sum(1 for _ in open(file_path)) - 1
                            if total_rows > max_rows:
                                result.append(f"  ... ({format_number(total_rows)} total rows)")
                        except:
                            pass
                            
                        return "\n".join(result)
                        
                    except ImportError:
                        # Fallback to basic CSV/TSV reading
                        import csv
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            reader = csv.reader(f, delimiter=delimiter)
                            rows = []
                            for i, row in enumerate(reader):
                                if i > max_rows:
                                    break
                                rows.append(row)
                            
                            if not rows:
                                file_type = "TSV" if file_ext == '.tsv' else "CSV"
                                return f"[Empty {file_type} file]"
                            
                            result = []
                            result.append(format_column_list(rows[0], max_display=8))
                            
                            result.append("Data rows:")
                            for row in rows[1:max_rows+1]:
                                if len(row) > MAX_COLUMNS_DISPLAY:
                                    display_values = row[:MAX_COLUMNS_DISPLAY//2] + ['...'] + row[-MAX_COLUMNS_DISPLAY//2:]
                                else:
                                    display_values = row
                                
                                display_values = [truncate_string(v, MAX_CELL_LENGTH) for v in display_values]
                                row_str = ' | '.join(display_values)
                                
                                if len(row_str) > MAX_TOTAL_LINE_LENGTH:
                                    row_str = row_str[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                                result.append(f"  {row_str}")
                                
                            return "\n".join(result)
                            
                except Exception as e:
                    file_type = "TSV" if file_path.suffix.lower() == '.tsv' else "CSV"
                    return f"[Error reading {file_type}: {str(e)[:100]}]"
            
            def read_bioinformatics_sample(file_path, max_lines=8):
                """Read bioinformatics files with format-specific handling"""
                try:
                    ext = file_path.suffix.lower()
                    file_size = file_path.stat().st_size
                    
                    result = [f"File size: {format_number(file_size)} bytes"]
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = []
                        
                        if ext == '.fam':
                            # FAM files: Family ID, Individual ID, Paternal ID, Maternal ID, Sex, Phenotype
                            result.append("Format: Family_ID Individual_ID Paternal_ID Maternal_ID Sex Phenotype")
                            result.append("\nSample entries:")
                            for i, line in enumerate(f):
                                if i >= max_lines:
                                    lines.append("...")
                                    break
                                line = line.strip()
                                if line and len(line) > MAX_TOTAL_LINE_LENGTH:
                                    line = line[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                                lines.append(f"  {line}")
                                
                        elif ext == '.bim':
                            # BIM files: Chromosome, Variant ID, Genetic distance, Position, Allele1, Allele2
                            result.append("Format: Chromosome Variant_ID Genetic_distance Position Allele1 Allele2")
                            result.append("\nSample entries:")
                            for i, line in enumerate(f):
                                if i >= max_lines:
                                    lines.append("...")
                                    break
                                line = line.strip()
                                if line and len(line) > MAX_TOTAL_LINE_LENGTH:
                                    line = line[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                                lines.append(f"  {line}")
                                
                        elif ext == '.bed':
                            # BED files are binary, show file info only
                            result.append("Format: Binary PLINK genotype file")
                            result.append("Contains: Genotype data in binary format")
                            return "\n".join(result)
                            
                        elif ext in ['.vcf', '.vcf.gz']:
                            result.append("Format: Variant Call Format")
                            result.append("\nSample lines:")
                            for i, line in enumerate(f):
                                if i >= max_lines:
                                    lines.append("...")
                                    break
                                line = line.strip()
                                if line.startswith('#'):
                                    lines.append(f"  {line[:MAX_TOTAL_LINE_LENGTH]}")
                                else:
                                    if len(line) > MAX_TOTAL_LINE_LENGTH:
                                        line = line[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                                    lines.append(f"  {line}")
                                    
                        else:
                            # Generic text-based bioinformatics file
                            result.append("\nSample content:")
                            for i, line in enumerate(f):
                                if i >= max_lines:
                                    lines.append("...")
                                    break
                                line = line.strip()
                                if len(line) > MAX_TOTAL_LINE_LENGTH:
                                    line = line[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                                lines.append(f"  {line}")
                        
                        result.extend(lines)
                        return "\n".join(result)
                        
                except Exception as e:
                    return f"[Error reading bioinformatics file: {str(e)[:100]}]"
            
            def read_excel_sample(file_path, max_rows=MAX_CSV_ROWS):
                """Read Excel file with multiple fallback methods"""
                try:
                    # Method 1: Try pandas
                    try:
                        import pandas as pd
                        
                        excel_file = pd.ExcelFile(file_path)
                        sheets = excel_file.sheet_names
                        
                        result = []
                        result.append(f"Excel file with {len(sheets)} sheet(s): {', '.join(sheets[:5])}")
                        
                        if sheets:
                            df = pd.read_excel(file_path, sheet_name=sheets[0], nrows=max_rows + 1)
                            result.append(f"\nSheet '{sheets[0]}':")
                            result.append(f"Shape: ({df.shape[0]} rows, {df.shape[1]} cols)")
                            result.append(format_column_list(df.columns.tolist()))
                            
                            if len(df.columns) > MAX_COLUMNS_DISPLAY:
                                keep_cols = MAX_COLUMNS_DISPLAY // 2
                                display_cols = list(df.columns[:keep_cols]) + list(df.columns[-keep_cols:])
                                df_display = df[display_cols].copy()
                                df_display.insert(keep_cols, '...', '...')
                            else:
                                df_display = df.copy()
                            
                            for col in df_display.columns:
                                if col != '...':
                                    df_display[col] = df_display[col].apply(lambda x: truncate_string(x, MAX_CELL_LENGTH))
                            
                            result.append("\nFirst rows:")
                            for idx, row in df_display.head(max_rows).iterrows():
                                row_str = ' | '.join([truncate_string(str(v), MAX_CELL_LENGTH) for v in row.values])
                                if len(row_str) > MAX_TOTAL_LINE_LENGTH:
                                    row_str = row_str[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                                result.append(f"  {row_str}")
                            
                            if len(df) > max_rows:
                                result.append(f"  ... (more rows available)")
                                
                        return "\n".join(result)
                        
                    except ImportError:
                        pass
                    
                    # Method 2: Try openpyxl
                    try:
                        import openpyxl
                        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                        
                        result = []
                        result.append(f"Excel file with {len(wb.sheetnames)} sheet(s): {', '.join(wb.sheetnames[:5])}")
                        
                        sheet = wb.active
                        result.append(f"\nActive sheet: '{sheet.title}'")
                        
                        # Get dimensions
                        max_row = min(sheet.max_row, max_rows + 1)
                        max_col = sheet.max_column
                        result.append(f"Shape: (approx {sheet.max_row} rows, {max_col} cols)")
                        
                        # Read headers
                        headers = []
                        for cell in sheet[1]:
                            if cell.value is not None:
                                headers.append(str(cell.value))
                        
                        if headers:
                            result.append(format_column_list(headers))
                        
                        # Read sample rows
                        result.append("\nFirst rows:")
                        for row_idx in range(2, min(max_row + 1, max_rows + 2)):
                            row_values = []
                            col_count = 0
                            for cell in sheet[row_idx]:
                                if col_count >= MAX_COLUMNS_DISPLAY:
                                    if col_count == MAX_COLUMNS_DISPLAY:
                                        row_values.append('...')
                                    break
                                if cell.value is not None:
                                    row_values.append(truncate_string(str(cell.value), MAX_CELL_LENGTH))
                                else:
                                    row_values.append('')
                                col_count += 1
                            
                            row_str = ' | '.join(row_values)
                            if len(row_str) > MAX_TOTAL_LINE_LENGTH:
                                row_str = row_str[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                            result.append(f"  {row_str}")
                        
                        wb.close()
                        return "\n".join(result)
                        
                    except ImportError:
                        pass
                    
                    # Method 3: Basic file info only
                    file_size = file_path.stat().st_size
                    return f"[Excel file - {format_number(file_size)} bytes - install pandas or openpyxl for preview]"
                    
                except Exception as e:
                    return f"[Error reading Excel: {str(e)[:100]}]"
            
            def read_json_sample(file_path, max_lines=8):
                """Read JSON file sample"""
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)
                        
                        result = []
                        
                        if isinstance(data, dict):
                            keys = list(data.keys())
                            if len(keys) > 10:
                                display_keys = keys[:5] + ['...'] + keys[-3:]
                            else:
                                display_keys = keys
                            result.append(f"JSON object with {len(keys)} keys: {', '.join(display_keys)}")
                        elif isinstance(data, list):
                            result.append(f"JSON array with {len(data)} items")
                            if data and isinstance(data[0], dict):
                                keys = list(data[0].keys())
                                result.append(format_column_list(keys, max_display=8))
                        
                        json_str = json.dumps(data, indent=2, ensure_ascii=False)
                        lines = json_str.splitlines()[:max_lines]
                        lines = [l[:MAX_TOTAL_LINE_LENGTH-3] + "..." if len(l) > MAX_TOTAL_LINE_LENGTH else l for l in lines]
                        
                        if len(json_str.splitlines()) > max_lines:
                            lines.append("...")
                            
                        result.append("\nSample:")
                        result.extend(lines)
                        
                        return "\n".join(result)
                        
                except Exception as e:
                    return f"[Error reading JSON: {str(e)[:100]}]"
            
            def read_text_sample(file_path, max_lines=5):
                """Read text file sample"""
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = []
                        for i, line in enumerate(f):
                            if i >= max_lines:
                                lines.append("...")
                                break
                            line = line.rstrip()
                            if len(line) > MAX_TOTAL_LINE_LENGTH:
                                line = line[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                            lines.append(line)
                        return "\n".join(lines)
                except Exception as e:
                    return f"[Error reading: {str(e)[:50]}]"
            
            def read_structure_file(file_path, max_lines=8):
                """Read molecular structure files"""
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = []
                        for i, line in enumerate(f):
                            if i >= max_lines:
                                lines.append("...")
                                break
                            line = line.rstrip()
                            if len(line) > MAX_TOTAL_LINE_LENGTH:
                                line = line[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                            lines.append(line)
                        return "\n".join(lines)
                except Exception as e:
                    return f"[Error reading: {str(e)[:50]}]"
            
            def analyze_directory_pattern(dirs):
                """Detect directory patterns"""
                if len(dirs) < 3:
                    return None
                    
                numeric_dirs = [d for d in dirs if d.name.isdigit()]
                if len(numeric_dirs) >= len(dirs) * 0.7:
                    sorted_nums = sorted([int(d.name) for d in numeric_dirs])
                    return {
                        'type': 'numeric',
                        'count': len(numeric_dirs),
                        'range': f"{sorted_nums[0]}-{sorted_nums[-1]}",
                        'samples': sorted_nums[:NUMERIC_DIR_SAMPLES]
                    }
                
                return None
            
            def should_show_content_sample(category, file_ext):
                """Determine if we should show content sample for this file type"""
                if category in ['data', 'bioinformatics', 'structure']:
                    return content_samples_per_type[file_ext] < MAX_CONTENT_SAMPLES_PER_TYPE
                return False
            
            def process_directory(dir_path, level=0, parent_pattern=None):
                """Process directory with samples from all important files"""
                
                if level > MAX_DEPTH:
                    return
                
                indent = "  " * level
                
                try:
                    items = list(dir_path.iterdir())
                    files = [i for i in items if i.is_file()]
                    dirs = sorted([i for i in items if i.is_dir()], key=lambda x: x.name)[:MAX_DIRS_PER_LEVEL]
                    
                    # Display directory name with full path
                    rel_path = dir_path.relative_to(data_path) if dir_path != data_path else Path(".")
                    if level == 0:
                        lines.append(f"{data_path.name}/ (root)")
                    else:
                        lines.append(f"{indent}{rel_path.name}/")
                        # Also show the relative path for deeper directories
                        if level > 1:
                            lines.append(f"{indent}  [Path: {rel_path}]")
                    
                    # Analyze directory pattern
                    pattern = analyze_directory_pattern(dirs)
                    
                    if pattern and pattern['type'] == 'numeric':
                        lines.append(f"{indent}  [Numeric pattern: {pattern['count']} directories, range {pattern['range']}]")
                        sample_dirs = [d for d in dirs if d.name == str(pattern['samples'][0])]
                        if sample_dirs:
                            sample_dir = sample_dirs[0]
                            lines.append(f"{indent}  Sample from directory '{sample_dir.name}':")
                            process_directory(sample_dir, level + 1, pattern)
                            return  # Don't process other subdirectories if numeric pattern
                    
                    # Process files by category
                    file_categories = defaultdict(list)
                    for f in files:
                        category = get_file_category(f.suffix)
                        file_categories[category].append(f)
                    
                    # Process each category with guaranteed samples for important types
                    for category, cat_files in file_categories.items():
                        if category == 'image':
                            # Show image files with examples
                            lines.append(f"{indent}  📷 Images: {len(cat_files)} files")
                            by_ext = defaultdict(list)
                            for f in cat_files:
                                by_ext[f.suffix.lower()].append(f.name)
                            
                            for ext, names in by_ext.items():
                                sample_names = sorted(names)[:MAX_IMAGE_EXAMPLES]
                                lines.append(f"{indent}    {ext} ({len(names)} files): {', '.join(sample_names)}")
                                if len(names) > MAX_IMAGE_EXAMPLES:
                                    lines.append(f"{indent}      ... and {len(names) - MAX_IMAGE_EXAMPLES} more")
                        
                        elif category in ['data', 'bioinformatics', 'structure']:
                            # Show ALL important data files with content preview
                            icon = "🧬" if category == "bioinformatics" else "📊" if category == "data" else "🔬"
                            lines.append(f"{indent}  {icon} {category.title()} files: {len(cat_files)} files")
                            
                            # Group by extension
                            by_ext = defaultdict(list)
                            for f in cat_files:
                                by_ext[f.suffix.lower()].append(f)
                            
                            # Process each extension type
                            for ext, ext_files in by_ext.items():
                                # Sort files by importance
                                priority_order = {
                                    'train': 1, 'test': 2, 'val': 3, 'validation': 3,
                                    'data': 4, 'dataset': 5, 'metadata': 6
                                }
                                
                                def get_priority(file_path):
                                    stem_lower = file_path.stem.lower()
                                    for keyword, priority in priority_order.items():
                                        if keyword in stem_lower:
                                            return priority
                                    return 999
                                
                                sorted_files = sorted(ext_files, key=get_priority)
                                
                                # Show samples - ensure at least one per extension
                                files_to_show = sorted_files[:max(1, MAX_CONTENT_SAMPLES_PER_TYPE)]
                                
                                for file_idx, sample_file in enumerate(files_to_show):
                                    if not should_show_content_sample(category, ext) and file_idx > 0:
                                        break
                                        
                                    lines.append(f"{indent}    📄 [{sample_file.name}]")
                                    
                                    # Read content based on file type and category
                                    if category == 'bioinformatics':
                                        content = read_bioinformatics_sample(sample_file, max_lines=5 if file_idx > 0 else 8)
                                    elif ext in ['.csv', '.tsv']:
                                        content = read_tabular_sample(sample_file, max_rows=3 if file_idx > 0 else 5)
                                    elif ext in ['.xlsx', '.xls']:
                                        content = read_excel_sample(sample_file, max_rows=3 if file_idx > 0 else 5)
                                    elif ext == '.json':
                                        content = read_json_sample(sample_file, max_lines=5 if file_idx > 0 else 8)
                                    elif ext in ['.txt', '.md']:
                                        content = read_text_sample(sample_file, max_lines=3 if file_idx > 0 else 5)
                                    elif category == 'structure':
                                        content = read_structure_file(sample_file, max_lines=6)
                                    else:
                                        size = sample_file.stat().st_size
                                        content = f"[{ext} file - {format_number(size)} bytes]"
                                    
                                    # Add content with indentation
                                    for line in content.splitlines():
                                        if len(line) > MAX_TOTAL_LINE_LENGTH:
                                            line = line[:MAX_TOTAL_LINE_LENGTH-3] + "..."
                                        lines.append(f"{indent}      {line}")
                                    
                                    content_samples_per_type[ext] += 1
                                
                                # List remaining files if any
                                if len(ext_files) > len(files_to_show):
                                    remaining = len(ext_files) - len(files_to_show)
                                    remaining_names = [f.name for f in sorted_files[len(files_to_show):len(files_to_show)+3]]
                                    if remaining_names:
                                        lines.append(f"{indent}    📋 Other {ext} files: {', '.join(remaining_names)}")
                                        if remaining > 3:
                                            lines.append(f"{indent}      ... and {remaining - 3} more {ext} files")
                        
                        elif category in ['code', 'config', 'doc', 'model']:
                            icons = {'code': '💻', 'config': '⚙️', 'doc': '📖', 'model': '🤖'}
                            lines.append(f"{indent}  {icons.get(category, '📄')} {category.title()} files: {len(cat_files)}")
                            sample_names = [f.name for f in cat_files[:5]]
                            lines.append(f"{indent}    Files: {', '.join(sample_names)}")
                            if len(cat_files) > 5:
                                lines.append(f"{indent}    ... and {len(cat_files) - 5} more")
                        
                        elif category == 'other' and cat_files:
                            lines.append(f"{indent}  📄 Other files: {len(cat_files)}")
                            sample_names = [f.name for f in cat_files[:5]]
                            lines.append(f"{indent}    Files: {', '.join(sample_names)}")
                            if len(cat_files) > 5:
                                lines.append(f"{indent}    ... and {len(cat_files) - 5} more")
                    
                    # Process subdirectories
                    if not pattern:
                        for subdir in dirs:
                            process_directory(subdir, level + 1)
                
                except PermissionError:
                    lines.append(f"{indent}  [Permission denied]")
                except Exception as e:
                    lines.append(f"{indent}  [Error: {str(e)[:50]}]")
            
            # Start processing
            lines.append("=== DATA STRUCTURE ===")
            lines.append("")
            process_directory(data_path)
            
            # Add summary
            lines.append("")
            lines.append("=== SUMMARY ===")
            
            # Quick statistics
            total_files = 0
            file_types = Counter()
            category_counts = Counter()
            
            for root, dirs, files in os.walk(data_path):
                depth = len(Path(root).relative_to(data_path).parts)
                if depth > MAX_DEPTH:
                    continue
                
                for f in files:
                    total_files += 1
                    ext = Path(f).suffix.lower()
                    category = get_file_category(ext)
                    
                    if ext:
                        file_types[ext] += 1
                    category_counts[category] += 1
                
                if total_files > 10000:
                    total_files = ">10K"
                    break
            
            lines.append(f"📊 Total files: {format_number(total_files) if isinstance(total_files, int) else total_files}")
            if file_types:
                lines.append(f"📋 File types: {', '.join(f'{e}:{format_number(c)}' for e, c in file_types.most_common(8))}")
            if category_counts:
                lines.append(f"📂 Categories: {', '.join(f'{cat}:{format_number(count)}' for cat, count in category_counts.most_common())}")
            
            total_samples = sum(content_samples_per_type.values())
            lines.append(f"👁️ Content samples shown: {total_samples}")
            if content_samples_per_type:
                samples_by_type = ', '.join(f'{ext}:{count}' for ext, count in content_samples_per_type.items())
                lines.append(f"🔍 Samples by type: {samples_by_type}")
            
            return "\n".join(lines)


    async def __call__(self, task_data: Dict[str, Any], datasets_dir: str, work_path: str, 
                    include_workflow: bool = False, include_domain_knowledge: bool = False):
        """
        MoSci Analysis operator - 分析科学发现任务
        
        Args:
            task_data: 科学发现任务数据字典，包含background, hypothesis, workflow等
            datasets_dir: 数据集目录路径
            work_path: 工作路径，用于保存分析结果和中间文件
            include_workflow: 是否包含workflow信息到prompt中 (default: False)
            include_domain_knowledge: 是否包含domain_knowledge信息到prompt中 (default: False)
        
        Returns:
            Dict包含thought和plan字段
        """
        task_id = task_data.get('id', 'unknown')
        logger.info(f"Analyzing scientific discovery task {task_id} by exploring data directory...")
        
        data_path = Path(datasets_dir)
        work_dir = Path(work_path)
        
        # 确保工作目录存在
        work_dir.mkdir(parents=True, exist_ok=True)
        

        
        # 1. 生成数据描述
        data_description = self._generate_data_description(data_path)
        
        # 2. 从task_data中提取科学发现相关信息
        task_id = task_data.get('id', 'unknown')
        background = task_data.get('background', '')
        hypothesis = task_data.get('hypothesis', '')
        answer_format = task_data.get('answer_format', '')
        scientific_domain = task_data.get('scientific_domain', '')
        task_type = task_data.get('task_type', '')
        
        # 可选信息（根据开关决定是否包含）
        workflow = task_data.get('workflow', '') if include_workflow else ''
        domain_knowledge = task_data.get('domain_knowledge', '') if include_domain_knowledge else ''
        
        # 4. 格式化scientific discovery prompt
        prompt = SCIENTIFIC_DISCOVERY_ANALYSIS_PROMPT.format(
            task_id=task_id,
            scientific_domain=scientific_domain,
            background=background,
            hypothesis=hypothesis,
            datasets_dir=datasets_dir,
            work_path=work_path,
            data_files_summary=data_description,
            answer_format=answer_format,
            workflow=workflow,
            domain_knowledge=domain_knowledge
        )
        
        # Returns dict matching AnalysisOp: {"thought": "...", "plan": "..."}
        response = await self._fill_node(AnalysisOp, prompt, mode="xml_fill")

            # Save analysis results to workspace as JSON
        try:
            work_dir = Path(work_path)
            
            # Prepare analysis data
            analysis_data = {
                "task_id": task_data.get('id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "operator": "Analysis",
                "prompt": prompt,
                "thought": response.get("thought", ""),
                "plan": response.get("plan", ""),
                "include_workflow": include_workflow,
                "include_domain_knowledge": include_domain_knowledge,
                "datasets_dir": datasets_dir
            }
            
            # Save as JSON
            analysis_file = work_dir / "analysis_results.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Analysis results saved to: {analysis_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save analysis results: {e}")
        return response



class CodeGenerate(Operator):
    def __init__(self, llm: AsyncLLM, name: str = "CodeGenerate"):
        super().__init__(llm, name)

    async def __call__(self, task_data: Dict[str, Any], datasets_dir: str, work_path: str, plan: str, prev_code: str = "", exec_result: Dict = None):
        """
        MoSci CodeGenerate operator - 生成科学分析代码
        
        Args:
            task_data: 科学发现任务数据字典
            datasets_dir: 数据集目录路径
            work_path: 工作路径
            plan: 分析计划
            prev_code: 之前的代码（用于refinement）
            exec_result: 执行结果（用于refinement）
        
        Returns:
            Dict包含response或python_code字段
        """
        task_id = task_data.get('id', 'unknown')
        answer_format = task_data.get('answer_format', '')
        
        if exec_result:
            logger.info(f"Refining scientific analysis code for task {task_id} based on execution error...")
            # 使用科学发现的CodeRefine prompt（需要创建新的或修改现有的）
            prompt = SCIENTIFIC_CODE_REFINE_PROMPT.format(
                plan=plan,
                answer_format=answer_format,
                datasets_dir=datasets_dir,
                work_path=work_path,
                code=prev_code,
                success=exec_result.get("success", False),
                error=exec_result.get("error", "N/A"),
                stdout=exec_result.get("stdout", ""),
                stderr=exec_result.get("stderr", ""),
            )
        else:
            logger.info(f"Generating scientific analysis code for task {task_id}...")
            
            # 使用简化的科学发现CodeGenerate prompt
            prompt = SCIENTIFIC_CODE_GENERATE_PROMPT.format(
                plan=plan,
                answer_format=answer_format,
                datasets_dir=datasets_dir,
                work_path=work_path
            )

        response = await self._fill_node(CodeGenerateOp, prompt, mode="code_fill")

            # Save code generation results to workspace as JSON
        try:
            work_dir = Path(work_path)
            
            # Prepare code generation data
            code_data = {
                "task_id": task_data.get('id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "operator": "CodeGenerate",
                "prompt": prompt,
                "thought": response.get("thought", ""),
                "python_code": response.get("python_code") or response.get("response", ""),
                "plan": plan,
                "is_refinement": bool(exec_result),
                "prev_code": prev_code if prev_code else None,
                "exec_result": exec_result if exec_result else None
            }
            
            # Save as JSON
            code_gen_file = work_dir / "code_generation_results.json"
            with open(code_gen_file, 'w', encoding='utf-8') as f:
                json.dump(code_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Code generation results saved to: {code_gen_file}")
            
            # Also save the code separately for execution
            code = response.get("python_code") or response.get("response", "")
            if code:
                code_file = work_dir / "generated_code.py"
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(code)
                logger.info(f"Generated code saved to: {code_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save code generation results: {e}")
        return response


class CodeExecute(Operator):
    """ Executes python code string in a subprocess. Does NOT call LLM."""
    
    def __init__(self, llm: Optional[AsyncLLM] = None, name: str = "CodeExecute"):
        # LLM is optional here
        super().__init__(llm, name)
    
    async def __call__(self, code: str, output_dir: str, timeout: int = 600, 
                      realtime_output: bool = True,
                      output_callback: Optional[Callable[[str, str], None]] = None) -> Dict[str, Any]:
        """
        Executes the given code and returns results for scientific discovery tasks.
        SECURITY WARNING: Executing arbitrary code is dangerous. 
        Use sandboxing (e.g., Docker) in production.
        
        Args:
            code: Python code to execute
            output_dir: Directory where the code will be executed (work_path)
            timeout: Maximum execution time in seconds
            realtime_output: Enable real-time output display (default: True)
            output_callback: Custom callback for real-time output (content, stream_type)
                           If None and realtime_output=True, uses default print callback
        """
        
        # 【保留重要步骤】使用CODE_EXECUTE_PROMPT清理和格式化代码
        logger.info(f"Generating execute code ...")
        prompt = CODE_EXECUTE_PROMPT.format(
            code=code
        )
        response = await self._fill_node(CodeExecuteOp, prompt, mode="code_fill")
        code = response.get("python_code", code) or response.get("response", "") # Fallback to original if not provided
        
        logger.info(f"Executing scientific analysis code (timeout={timeout}s)...")
        
        temp_file = None
        process = None
        stdout, stderr = b"", b""
        success = False
        error_msg = None
        
        # 设置默认的实时输出回调，适配科学分析任务
        if realtime_output and output_callback is None:
            def default_output_callback(content: str, stream_type: str):
                if stream_type == "STDOUT":
                    print(f"\033[32m[SCIENTIFIC-{stream_type}]\033[0m {content}")  # 绿色
                else:  # STDERR
                    print(f"\033[31m[SCIENTIFIC-{stream_type}]\033[0m {content}")  # 红色
            output_callback = default_output_callback
        elif not realtime_output:
            output_callback = None
        
        # 用于收集所有输出的列表
        all_stdout = []
        all_stderr = []
        
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 创建科学分析脚本文件
            temp_file = os.path.join(output_dir, "scientific_analysis.py")
            with open(temp_file, "w", encoding='utf-8') as fp:
                fp.write(code)
                fp.flush() # Ensure content is written
            
            logger.info(f"Scientific analysis script saved to: {temp_file}")
            
            # Create the subprocess
            process = await asyncio.create_subprocess_exec(
                sys.executable,  # Use the current Python interpreter
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                # 使用work_path作为工作目录，确保科学分析结果保存在正确位置
                cwd=output_dir
            )
            
            # 实时读取流的异步函数
            async def read_stream_realtime(stream, stream_name: str, output_list: list):
                """实时读取流输出"""
                try:
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        
                        line_str = line.decode('utf-8', errors='ignore')
                        output_list.append(line_str)
                        
                        # 实时输出回调
                        if output_callback:
                            output_callback(line_str.rstrip(), stream_name)
                        
                except Exception as e:
                    logger.error(f"Error reading {stream_name} stream: {e}")
            
            # Wait for the process to complete with a timeout
            try:
                # 创建实时读取任务
                stdout_task = asyncio.create_task(
                    read_stream_realtime(process.stdout, "STDOUT", all_stdout)
                )
                stderr_task = asyncio.create_task(
                    read_stream_realtime(process.stderr, "STDERR", all_stderr)
                )
                
                # 等待进程完成
                await asyncio.wait_for(process.wait(), timeout=timeout)
                
                # 等待流读取完成
                await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)
                
                # 重新构建stdout和stderr字节串以保持原有返回格式
                stdout = "".join(all_stdout).encode('utf-8')
                stderr = "".join(all_stderr).encode('utf-8')
                
                success = (process.returncode == 0)
                if not success:
                    error_msg = f"Scientific analysis failed with return code: {process.returncode}"
                    logger.warning(f"Scientific code execution failed: {error_msg}")
                else:
                    logger.info(f"Scientific analysis completed successfully")
                    
            except asyncio.TimeoutError:
                logger.warning(f"Scientific analysis timed out after {timeout}s.")
                error_msg = f"Scientific analysis timeout after {timeout} seconds"
                if process:
                    try:
                        process.kill() # Force kill
                        # 等待流读取任务完成，即使超时也尝试获取部分输出
                        try:
                            await asyncio.wait_for(
                                asyncio.gather(stdout_task, stderr_task, return_exceptions=True),
                                timeout=1.0  # 给1秒时间收集部分输出
                            )
                        except asyncio.TimeoutError:
                            pass
                        
                        # 重新构建输出
                        stdout = "".join(all_stdout).encode('utf-8')
                        stderr = "".join(all_stderr).encode('utf-8')
                        
                    except Exception:
                        pass # ignore errors during kill/communicate on timeout
                success = False
                
        except Exception as e:
            error_msg = f"Error setting up/running scientific analysis: {type(e).__name__}: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            success = False
        finally:
            # 保留科学分析脚本文件，方便调试和审查
            if temp_file and os.path.exists(temp_file):
                logger.info(f"Scientific analysis script preserved at: {temp_file}")
        
        # 检查是否生成了预期的结果文件
        results_file = os.path.join(output_dir, "scientific_computation_results.txt")
        if success and os.path.exists(results_file):
            logger.info(f"Scientific computation results saved to: {results_file}")
        elif success:
            logger.warning(f"Scientific analysis completed but results file not found: {results_file}")
        
        return {
            "success": success,
            "stdout": stdout.decode(errors='ignore'),
            "stderr": stderr.decode(errors='ignore'),
            "error": error_msg,
            "returncode": process.returncode if process else -1
        }



class CodeRefine(Operator):
    def __init__(self, llm: AsyncLLM, name: str = "CodeRefine", max_output_chars: int = 2000):
        super().__init__(llm, name)
        self.max_output_chars = max_output_chars
    
    def _truncate_output(self, output: str, max_chars: int) -> str:
        """
        截断输出内容，保留后面的部分（通常更重要）
        如果内容过长，会添加截断提示
        """
        if not output or len(output) <= max_chars:
            return output
        
        # 保留后面的内容
        truncated = output[-max_chars:]
        
        # 添加截断提示
        truncation_notice = "[...Content truncated, showing last {} characters...]\n".format(max_chars)
        
        # 确保截断提示不会超过总长度
        if len(truncation_notice) < max_chars:
            final_content = truncation_notice + truncated[len(truncation_notice):]
        else:
            final_content = truncated
            
        return final_content
    
    async def __call__(self, task_data: Dict[str, Any], datasets_dir: str, work_path: str, 
                      plan: str, prev_code: str, exec_result: Dict):
        """
        MoSci CodeRefine operator - 修复科学分析代码
        
        Args:
            task_data: 科学发现任务数据字典
            datasets_dir: 数据集目录路径
            work_path: 工作路径
            plan: 分析计划
            prev_code: 需要修复的代码
            exec_result: 执行结果（包含错误信息）
        
        Returns:
            Dict包含response或python_code字段
        """
        task_id = task_data.get('id', 'unknown')
        answer_format = task_data.get('answer_format', '')
        
        logger.info(f"Refining scientific analysis code for task {task_id} based on execution error...")
        
        # 获取原始输出
        raw_stdout = exec_result.get("stdout", "")
        raw_stderr = exec_result.get("stderr", "")
        
        # 截断过长的输出
        truncated_stdout = self._truncate_output(raw_stdout, self.max_output_chars)
        truncated_stderr = self._truncate_output(raw_stderr, self.max_output_chars)
        
        # 记录截断信息
        if len(raw_stdout) > self.max_output_chars:
            logger.info(f"Scientific analysis stdout truncated from {len(raw_stdout)} to {len(truncated_stdout)} chars")
        if len(raw_stderr) > self.max_output_chars:
            logger.info(f"Scientific analysis stderr truncated from {len(raw_stderr)} to {len(truncated_stderr)} chars")
        
        # 使用科学发现特定的代码修复prompt
        prompt = SCIENTIFIC_CODE_REFINE_PROMPT.format(
            plan=plan,
            answer_format=answer_format,
            datasets_dir=datasets_dir,
            work_path=work_path,
            code=prev_code,
            success=exec_result.get("success", False),
            error=exec_result.get("error", "N/A"),
            stdout=truncated_stdout,
            stderr=truncated_stderr,
        )
                 
        response = await self._fill_node(CodeRefineOp, prompt, mode="xml_fill")


        # Save code refinement results to workspace as JSON
        try:
            work_dir = Path(work_path)
            
            # Prepare code refinement data
            refine_data = {
                "task_id": task_data.get('id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "operator": "CodeRefine",
                "prompt": prompt,
                "thought": response.get("thought", ""),
                "python_code": response.get("python_code") or response.get("response", ""),
                "plan": plan,
                "prev_code": prev_code,
                "exec_result": {
                    "success": exec_result.get("success", False),
                    "error": exec_result.get("error", ""),
                    "stdout_length": len(exec_result.get("stdout", "")),
                    "stderr_length": len(exec_result.get("stderr", "")),
                    "returncode": exec_result.get("returncode", -1)
                },
                "stdout_truncated": truncated_stdout,
                "stderr_truncated": truncated_stderr
            }
            
            # Save as JSON
            refine_file = work_dir / "code_refinement_results.json"
            with open(refine_file, 'w', encoding='utf-8') as f:
                json.dump(refine_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Code refinement results saved to: {refine_file}")
            
            # Also save the refined code separately
            code = response.get("python_code") or response.get("response", "")
            if code:
                refined_code_file = work_dir / "refined_code.py"
                with open(refined_code_file, 'w', encoding='utf-8') as f:
                    f.write(code)
                logger.info(f"Refined code saved to: {refined_code_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save code refinement results: {e}")
        return response





class ScientificConclusion(Operator):
    """Generate scientific conclusion and format answer based on analysis results."""
    def __init__(self, llm: AsyncLLM, name: str = "ScientificConclusion"):
        super().__init__(llm, name)

    async def __call__(self, task_data: Dict[str, Any], work_path: str):
        """
        MoSci ScientificConclusion operator - 生成科学结论并格式化答案
        
        Args:
            task_data: 科学发现任务数据字典，包含answer_format等信息
            work_path: 工作路径，包含科学分析结果文件
        
        Returns:
            Dict包含formatted_answer或response字段
        """
        task_id = task_data.get('id', 'unknown')
        answer_format = task_data.get('answer_format', '')
        background = task_data.get('background', '')
        hypothesis = task_data.get('hypothesis', '')
        
        logger.info(f"Generating scientific conclusion from analysis results for task {task_id}")
        
        # 读取科学计算结果文件
        results_file = os.path.join(work_path, "scientific_computation_results.txt")
        analysis_results = ""
        
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    analysis_results = f.read()
                logger.info(f"Successfully loaded scientific results from: {results_file}")
            except Exception as e:
                logger.warning(f"Failed to read scientific results file: {e}")
                analysis_results = "[Error: Could not read scientific computation results]"
        else:
            logger.warning(f"Scientific results file not found: {results_file}")
            analysis_results = "[Warning: No scientific computation results file found]"
        
        # 检查work_path中的其他相关文件
        additional_files = []
        try:
            for file_path in Path(work_path).glob("*"):
                if file_path.is_file() and file_path.name != "scientific_computation_results.txt":
                    file_info = f"- {file_path.name} ({file_path.stat().st_size} bytes)"
                    additional_files.append(file_info)
        except Exception as e:
            logger.warning(f"Failed to scan work directory: {e}")
        
        additional_files_info = "\n".join(additional_files) if additional_files else "[No additional files found]"
        
        # 使用科学结论生成prompt
        prompt = SCIENTIFIC_CONCLUSION_PROMPT.format(
            task_id=task_id,
            background=background,
            hypothesis=hypothesis,
            answer_format=answer_format,
            work_path=work_path,
            analysis_results=analysis_results,
            additional_files=additional_files_info
        )
        
        logger.debug(f"Scientific conclusion prompt prepared for task: {task_id}")
        response = await self._fill_node(ScientificConclusionOp, prompt, mode="xml_fill")

            # Save scientific conclusion results to workspace as JSON
        try:
            work_dir = Path(work_path)
            
            # Prepare conclusion data
            conclusion_data = {
                "task_id": task_data.get('id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "operator": "ScientificConclusion",
                "prompt": prompt,
                "thought": response.get("thought", ""),
                "formatted_answer": response.get("formatted_answer", ""),
                "background": background,
                "hypothesis": hypothesis,
                "answer_format": answer_format,
                "analysis_results_length": len(analysis_results),
                "additional_files": additional_files_info,
                "has_critic_suggestions": bool(task_data.get('critic_suggestions'))
            }
            
            # Save as JSON
            conclusion_file = work_dir / "scientific_conclusion_results.json"
            with open(conclusion_file, 'w', encoding='utf-8') as f:
                json.dump(conclusion_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Scientific conclusion results saved to: {conclusion_file}")
            
            # Also save just the final answer separately for easy access
            if response.get("formatted_answer"):
                answer_file = work_dir / "final_answer.txt"
                with open(answer_file, 'w', encoding='utf-8') as f:
                    f.write(response["formatted_answer"])
                logger.info(f"Final answer saved to: {answer_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save scientific conclusion results: {e}")
        return response








class NoDataGuess(Operator):
    """NoDataGuess operator for making educated guesses about scientific hypotheses without accessing actual data."""
    def __init__(self, llm: AsyncLLM, name: str = "NoDataGuess"):
        super().__init__(llm, name)

    def _load_data_description(self, datasets_dir: str) -> str:
        """
        直接加载数据集目录上一级的data_description.json文件
        
        Args:
            datasets_dir: 数据集目录路径 (如: /path/to/data/health_spa/datasets)
            
        Returns:
            数据描述的JSON内容格式化为字符串
        """
        import json
        
        try:
            # 获取上一级目录中的data_description.json
            datasets_path = Path(datasets_dir)
            parent_dir = datasets_path.parent  # 上一级目录
            data_description_file = parent_dir / "data_description.json"
            
            logger.info(f"NoDataGuess: Looking for data description at: {data_description_file}")
            
            if not data_description_file.exists():
                logger.warning(f"NoDataGuess: data_description.json not found at {data_description_file}")
                return f"[Data description file not found at: {data_description_file}]"
            
            # 读取并解析JSON文件
            with open(data_description_file, 'r', encoding='utf-8') as f:
                data_desc = json.load(f)
            
            # 格式化数据描述为可读字符串
            formatted_desc = self._format_data_description(data_desc)
            logger.info(f"NoDataGuess: Successfully loaded data description for domain: {data_desc.get('domain', 'Unknown')}")
            
            return formatted_desc
            
        except json.JSONDecodeError as e:
            error_msg = f"[Error parsing data_description.json: {e}]"
            logger.error(f"NoDataGuess: {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"[Error loading data description: {e}]"
            logger.error(f"NoDataGuess: {error_msg}")
            return error_msg
    
    def _format_data_description(self, data_desc: dict) -> str:
        """
        将data_description.json内容格式化为可读的字符串
        
        Args:
            data_desc: 解析后的data_description.json内容
            
        Returns:
            格式化的数据描述字符串
        """
        description_lines = []
        
        # 基本信息
        description_lines.append("=== DATASET DESCRIPTION (From data_description.json) ===")
        description_lines.append(f"📊 Dataset ID: {data_desc.get('id', 'Unknown')}")
        description_lines.append(f"🔬 Scientific Domain: {data_desc.get('domain', 'Unknown')}")
        description_lines.append(f"📈 Data Modalities: {data_desc.get('modalities', 'Unknown')}")
        
        # 总体描述
        overall_desc = data_desc.get('overall_description', '')
        if overall_desc:
            description_lines.append(f"\n📋 Overall Description:")
            description_lines.append(f"   {overall_desc}")
        
        # 数据集详细信息
        datasets = data_desc.get('datasets', [])
        if datasets:
            description_lines.append(f"\n=== DATASET DETAILS ===")
            
            for i, dataset in enumerate(datasets, 1):
                dataset_name = dataset.get('name', f'Dataset {i}')
                dataset_desc = dataset.get('dataset_description', 'No description available')
                
                description_lines.append(f"\n📄 Dataset {i}: {dataset_name}")
                description_lines.append(f"   Description: {dataset_desc}")
                
                # 列信息
                columns = dataset.get('columns', [])
                if columns:
                    description_lines.append(f"   📊 Columns ({len(columns)} total):")
                    
                    for col in columns:
                        col_name = col.get('name', 'Unknown Column')
                        col_desc = col.get('description', 'No description')
                        description_lines.append(f"     • {col_name}: {col_desc}")
        
        # NoDataGuess特殊说明
        description_lines.append(f"\n=== NODATA GUESS CONTEXT ===")
        description_lines.append(f"🚫 This is a NoDataGuess baseline - using ONLY the above description")
        description_lines.append(f"📋 NO actual data files were accessed or analyzed")
        description_lines.append(f"🧠 Conclusions must be based purely on domain knowledge and this description")
        
        return "\n".join(description_lines)

    async def __call__(self, task_data: Dict[str, Any], datasets_dir: str, work_path: str):
        """
        NoDataGuess operator - 基于data_description.json和领域知识猜测科学假设结论
        
        Args:
            task_data: 科学发现任务数据字典
            datasets_dir: 数据集目录路径 (如: /path/to/health_spa/datasets)
            work_path: 工作路径，用于保存结果
        
        Returns:
            Dict包含thought, hypothesis_guess, formatted_answer字段
        """
        task_id = task_data.get('id', 'unknown')
        scientific_domain = task_data.get('scientific_domain', '')
        background = task_data.get('background', '')
        hypothesis = task_data.get('hypothesis', '')
        answer_format = task_data.get('answer_format', '')
        
        logger.info(f"NoDataGuess: Making educated guess for task {task_id} based on data_description.json only")
        
        # 直接加载data_description.json文件
        dataset_description = self._load_data_description(datasets_dir)
        
        # 使用NoDataGuess prompt
        prompt = NODATA_GUESS_PROMPT.format(
            task_id=task_id,
            scientific_domain=scientific_domain,
            dataset_description=dataset_description,
            background=background,
            hypothesis=hypothesis,
            answer_format=answer_format
        )
        
        response = await self._fill_node(NoDataGuessOp, prompt, mode="xml_fill")
        
        # Save NoDataGuess results to workspace as JSON
        try:
            work_dir = Path(work_path)
            work_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare NoDataGuess data
            nodata_guess_data = {
                "task_id": task_data.get('id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "operator": "NoDataGuess",
                "method": "data_description_json_only",
                "datasets_dir": datasets_dir,
                "data_description_source": str(Path(datasets_dir).parent / "data_description.json"),
                "prompt": prompt,
                "thought": response.get("thought", ""),
                "hypothesis_guess": response.get("hypothesis_guess", ""),
                "formatted_answer": response.get("formatted_answer", ""),
                "dataset_description": dataset_description,
                "scientific_domain": scientific_domain,
                "background": background,
                "hypothesis": hypothesis,
                "answer_format": answer_format
            }
            
            # Save as JSON
            nodata_guess_file = work_dir / "nodata_guess_results.json"
            with open(nodata_guess_file, 'w', encoding='utf-8') as f:
                json.dump(nodata_guess_data, f, indent=2, ensure_ascii=False)
            logger.info(f"NoDataGuess results saved to: {nodata_guess_file}")
            
            # Also save the final answer separately
            if response.get("formatted_answer"):
                answer_file = work_dir / "final_answer.txt"
                with open(answer_file, 'w', encoding='utf-8') as f:
                    f.write(response["formatted_answer"])
                logger.info(f"NoDataGuess final answer saved to: {answer_file}")
            
            # Save the loaded data description for reference
            desc_file = work_dir / "data_description_used.txt"
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(dataset_description)
            logger.info(f"NoDataGuess data description saved to: {desc_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save NoDataGuess results: {e}")
        
        return response
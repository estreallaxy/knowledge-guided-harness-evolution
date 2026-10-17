import base64
from pathlib import Path
from time import sleep

import pandas as pd
from PIL import Image
import io
import json
from typing import Dict, Any, Optional
import Evaluation
import re
from Config import *


class MathVista:
    def __init__(self, parquet_path: str):
    
        self.df = pd.read_parquet(parquet_path)
        self._current_idx = 0

    def _decode_image(self, image_bytes: bytes) -> Image.Image:

        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            return image
        except Exception as e:
            print(f"error：{str(e)}")
            return Image.new('RGB', (512, 512))

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        try:
            return json.loads(metadata_str)
        except:
            return {"context": ""}

    @property
    def current_entry(self) -> Dict[str, Any]:
        row = self.df.iloc[self._current_idx]

        return {
            "pid": row['pid'],
            "question": row['question'],
            "image_data": row['decoded_image']['bytes'],
            "image": self._decode_image(row['decoded_image']['bytes']),
            "choices": row['choices'],
            "unit": row['unit'],
            "precision": row['precision'],
            "answer": row['answer'],
            "question_type": row['question_type'],
            "answer_type": row['answer_type'],
            "metadata": row['metadata'],
            "query": row['query']
        }

    def move_next(self) -> bool:
        if self._current_idx < 6:
            self._current_idx += 1
            return True
        return False


class OlympiadBench:
    def __init__(self,
                 parquet_path: str,
                 sample_size: Optional[int] = None,
                 sample_id_file: Optional[str] = None,
                 random_state: int = 42):

        self.full_df = pd.read_parquet(parquet_path)
        self._current_idx = 0
        self.sample_id_file = sample_id_file

        if sample_size is not None:
            if sample_id_file and Path(sample_id_file).exists():
                self._load_sample_ids()
            else:
                self._perform_sampling(sample_size, random_state)
                if sample_id_file:
                    self._save_sample_ids()
        else:
            self.df = self.full_df.copy()

    def _perform_sampling(self, sample_size: int, random_state: int):
        if sample_size > len(self.full_df):
            raise ValueError(f"{sample_size} is larger than {len(self.full_df)}")

        self.df = self.full_df.sample(n=sample_size,
                                      random_state=random_state)
        print(f"sampling {sample_size} data")

    def _save_sample_ids(self):
        try:
            sample_ids = self.df['id'].tolist()
            with open(self.sample_id_file, 'w') as f:
                json.dump({
                    "metadata": {
                        "sample_size": len(sample_ids),
                        "created_at": pd.Timestamp.now().isoformat()
                    },
                    "sample_ids": sample_ids
                }, f, indent=2)
        except Exception as e:
            print(f"error：{str(e)}")

    def _load_sample_ids(self):
        try:
            with open(self.sample_id_file, 'r') as f:
                data = json.load(f)

            valid_ids = set(self.full_df['id'])
            loaded_ids = data['sample_ids']

            self.df = self.full_df[self.full_df['id'].isin(loaded_ids)]

            missing_ids = set(loaded_ids) - valid_ids
            if missing_ids:
                print(f"warning：{len(missing_ids)} not exists")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"failed：{str(e)}")

    def _decode_image(self, image_bytes: bytes) -> Image.Image:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            if image.mode == 'P':
                image = image.convert('RGB')
            return image
        except Exception as e:
            return Image.new('RGB', (512, 512))

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        try:
            return json.loads(metadata_str)
        except:
            return {"context": ""}

    @property
    def current_entry(self) -> Dict[str, Any]:
        row = self.df.iloc[self._current_idx]
        question = row['question']
        matches = [f"image_{m[0]}" for m in re.findall(r'<image_([^>]+)>', question)]

        entry = {
            "id": row['id'],
            "question": row['question'],
            "answer": row['final_answer'],
            "answer_type": row['answer_type'],
            "context": row['context'],
            "unit": row['unit'],
            "subfield": row['subfield'],
            "is_multiple_answer": row['is_multiple_answer']
        }
        for i in matches:
            entry[i] = self._decode_image(row[i]['bytes'])

        entry['num_img'] = len(matches)

        return entry

    def move_next(self) -> bool:
        if self._current_idx < len(self.df)-1:
            self._current_idx += 1
            return True
        return False


class EMMA:
    def __init__(self,
                 parquet_path: str,
                 sample_size: Optional[int] = None,
                 sample_id_file: Optional[str] = None,
                 random_state: int = 42):

        self.full_df = pd.read_parquet(parquet_path)
        self._current_idx = 0  # 统一从0开始

        if sample_size is not None:
            if sample_id_file and Path(sample_id_file).exists():
                self._load_sample_ids(sample_id_file)
            else:
                self._perform_sampling(sample_size, random_state)
                if sample_id_file:
                    self._save_sample_ids(sample_id_file)
        else:
            self.df = self.full_df.copy()

    def _perform_sampling(self, sample_size: int, random_state: int):
        if sample_size > len(self.full_df):
            raise ValueError("too large")

        self.df = self.full_df.sample(n=sample_size,
                                      random_state=random_state) \
            .reset_index(drop=True)

    def _save_sample_ids(self, file_path: str):
        sample_pids = self.df['pid'].tolist()
        with open(file_path, 'w') as f:
            json.dump({
                "metadata": {
                    "sample_size": len(sample_pids),
                    "created_at": pd.Timestamp.now().isoformat()
                },
                "sample_pids": sample_pids
            }, f, indent=2)

    def _load_sample_ids(self, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)

        valid_pids = set(self.full_df['pid'])
        loaded_pids = data['sample_pids']

        self.df = self.full_df[self.full_df['pid'].isin(loaded_pids)]
        self.df = self.df.reset_index(drop=True)

        missing = set(loaded_pids) - valid_pids
        if missing:
            print("warning")

    def _decode_image(self, image_bytes: bytes) -> Image.Image:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode in ['RGBA', 'P']:
                image = image.convert('RGB')
            return image
        except Exception as e:
            return Image.new('RGB', (512, 512))

    @property
    def current_entry(self) -> Dict[str, Any]:
        row = self.df.iloc[self._current_idx]
        return {
            "pid": row['pid'],
            "question": row['question'],
            "options": row['options'],
            "image_data": row['image_1']['bytes'],
            "image": self._decode_image(row['image_1']['bytes']),
            "category": row['category'],
            "answer": row['answer'],
            "type": row['type'],
            "source": row['source'],
            "context": row['context']
        }

    def move_next(self) -> bool:
        if self._current_idx < len(self.df)-1:
            self._current_idx += 1
            return True
        return False

    def reset(self):
        self._current_idx = 0

    def __len__(self):
        return len(self.df)


class EMMASpecial:
    def __init__(self, parquet_path: str):

        self.df = pd.read_parquet(parquet_path)
        self._current_idx = 0

    def _decode_image(self, image_bytes: bytes) -> Image.Image:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            return image
        except Exception as e:
            return Image.new('RGB', (512, 512)

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        try:
            return json.loads(metadata_str)
        except:
            return {"context": ""}

    @property
    def current_entry(self) -> Dict[str, Any]:
        row = self.df.iloc[self._current_idx]

        return {
            "pid": row['pid'],
            "question": row['question'],
            "options": row['options'],
            "image_data_1": row['image_1']['bytes'],
            "image_1": self._decode_image(row['image_1']['bytes']),
            "image_data_2": row['image_2']['bytes'],
            "image_2": self._decode_image(row['image_2']['bytes']),
            "image_data_3": row['image_3']['bytes'],
            "image_3": self._decode_image(row['image_3']['bytes']),
            "image_data_4": row['image_4']['bytes'],
            "image_4": self._decode_image(row['image_4']['bytes']),
            "image_data_5": row['image_5']['bytes'],
            "image_5": self._decode_image(row['image_5']['bytes']),
            "category": row['category'],
            "answer": row['answer'],
            "type": row['type'],
            "source": row['source'],
            "context": row['context']
        }

    def move_next(self) -> bool:
        if self._current_idx < 4:
            self._current_idx += 1
            return True
        return False







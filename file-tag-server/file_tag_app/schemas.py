from pydantic import BaseModel
from typing import List, Optional


# 标签crud
class tagBase(BaseModel):
    tag_name: str
    parent_tag_id: Optional[int] = None
    extra: str = None


class tag_create(tagBase):
    pass


class tag_delete(BaseModel):
    id: int


class tag_update(tagBase):
    id: int


# 文件crud
class fileBase(BaseModel):
    file_name: str
    abs_path: str
    extra: str


class file_create(fileBase):
    tags: List[int] = None


class multi_file_create(BaseModel):
    #  基于目录
    files: List[str] = None
    extra: str
    tags: List[int] = None


class file_delete(BaseModel):
    id: Optional[int]


class file_tags(BaseModel):
    file_id: int
    tags_id: List[int]
    direction: int
    # 1 表示添加, 2表示删除


class update_file(BaseModel):
    id: int
    file_name: str
    extra: str
    tags: List[int] = None

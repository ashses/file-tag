from sqlalchemy.orm import Session
from file_tag_app import models, schemas
from utilis.data import handle_query_data, get_datetime_formater, mime_to_simple_type
from sqlalchemy.exc import SQLAlchemyError
from utilis import system
import os
import magic
from typing import Optional


def create_tag(tag: schemas.tag_create, db: Session):
    try:
        tag_query_result = db.query(models.tag).filter_by(tag_name=tag.tag_name).first()
        if tag_query_result is not None:
            return handle_query_data(system.QUERY_BASE_ERROR, "标签名已经存在")
        if tag.parent_tag_id != -1:
            parentTagId = tag.parent_tag_id
        else:
            parentTagId = None
        if parentTagId is not None:
            parent_tag = db.query(models.tag).filter_by(id=parentTagId).first()
            if not parent_tag:
                parentTagId = None
        db_tag = models.tag(tag_name=tag.tag_name,
                            extra=tag.extra,
                            parent_tag_id=parentTagId)
        db.add(db_tag)
        db.commit()
        return handle_query_data(system.SUCCESS, "创建成功")
    except SQLAlchemyError as e:
        db.rollback()
        return handle_query_data(False, f"创建失败,发生异常:{e}")


def get_a_tag(param1: Optional[int], db: Session):
    db_tag = db.query(models.tag).filter_by(id=param1).first()
    if db_tag:
        return handle_query_data(system.SUCCESS, "", {
            "tag_name": db_tag.tag_name,
            "extra": db_tag.extra,
            "parent_id": db_tag.parent_tag_id if db_tag.parent_tag_id else -1,
            "parent_tag_name": db_tag.parent_tag.tag_name if db_tag.parent_tag else "根节点",
        })
    return handle_query_data(system.QUERY_BASE_ERROR, "查询对象不存在")


def update_tag(tag: schemas.tag_update, db: Session):
    try:
        db_tag = db.query(models.tag).filter_by(id=tag.id).first()
        if not db_tag:
            return handle_query_data(system.QUERY_BASE_ERROR, "对象不存在")
        if tag.tag_name != "":
            db_tag.tag_name = tag.tag_name
        if tag.extra != "":
            db_tag.extra = tag.extra
        if tag.parent_tag_id != -1 and tag.parent_tag_id > 0:
            db_tag.parent_tag_id = tag.parent_tag_id
        elif tag.parent_tag_id == -1:
            db_tag.parent_tag_id = None
        db.commit()
        return handle_query_data(system.SUCCESS, "更新成功")
    except SQLAlchemyError as e:
        db.rollback()
        return handle_query_data(system.QUERY_EXEC_ERROR, f"更新失败,发生异常{e}")


"""
想法1: 级联删除 - 当用户删除某个tag之后，会删除对应的子tag - 会产生，如果该tag下挂载的tag的递归太多，要删除较长的时间
想法2: 迁移 - 当用户删除某个tag之后, 不会删除对应的子tag，而是将子tag的父tag设置为tag的父tag。
"""


def delete_tag(tag_id: int, db: Session):
    try:
        db_tag_to_delete = db.query(models.tag).filter_by(id=tag_id).first()
        if not db_tag_to_delete:
            return handle_query_data(system.QUERY_BASE_ERROR, "对象不存在")
        parent_tag_id = db_tag_to_delete.parent_tag_id
        child_tag_id_list = []
        for child_tag in db_tag_to_delete.child_tags:
            child_tag_id_list.append(child_tag.id)
        db.delete(db_tag_to_delete)
        db.commit()
        for child_tag_id in child_tag_id_list:
            child_tag = db.query(models.tag).filter_by(id=child_tag_id).first()
            child_tag.parent_tag_id = parent_tag_id
            db.commit()
        return handle_query_data(system.SUCCESS, "删除成功")
    except SQLAlchemyError as e:
        db.rollback()
        return handle_query_data(system.QUERY_EXEC_ERROR, f"删除失败,发生异常:{e}")


def get_tag_list(db: Session):
    db_tag_list = db.query(models.tag).all()

    # 采用递归的方法来循环构建子标签
    def build_tag_hierarchy(tag):
        return {
            "id": tag.id,
            "tag_name": tag.tag_name,
            "create_time": get_datetime_formater(tag.create_time),
            "extra": tag.extra,
            "child_tags": [build_tag_hierarchy(child) for child in tag.child_tags]
        }

    data_list = [build_tag_hierarchy(t) for t in db_tag_list if t.parent_tag_id is None]
    return handle_query_data(system.SUCCESS, "", data_list)


def create_file(_file: schemas.file_create, db: Session):
    try:
        file_name = _file.file_name if (_file.file_name != "") \
            else _file.abs_path.split("/")[-1] \
            if len(_file.abs_path.split("/")) > 1 else _file.abs_path.split("\\")[-1]
        file_query_res = db.query(models.file).filter_by(abs_path=_file.abs_path).first()
        if file_query_res:
            return handle_query_data(system.QUERY_BASE_ERROR, "文件已经存在")
        if os.path.isdir(_file.abs_path):
            file_base_type = "目录"
            file_size = '0'
        else:
            with open(_file.abs_path, "rb") as f:
                buffer = f.read()
                mime_type = magic.from_buffer(buffer, mime=True)
            file_base_type = mime_to_simple_type.get(mime_type, "未知类型")
            file_size = os.path.getsize(_file.abs_path)
        db_file = models.file(
            file_name=file_name,
            abs_path=_file.abs_path,
            file_base_type=file_base_type,
            file_size=file_size,
            extra=_file.extra
        )
        tag_query_list = []
        for tag in _file.tags:
            tag_query_result = db.query(models.tag).filter_by(id=tag).first()
            if tag_query_result:
                tag_query_list.append(tag_query_result)
        db_file.tags = tag_query_list
        db.add(db_file)
        db.commit()
        return handle_query_data(system.SUCCESS, "添加成功")
    except SQLAlchemyError as e:
        db.rollback()
        return handle_query_data(system.QUERY_EXEC_ERROR, f"在添加数据库时发生异常,{e}")
    except FileNotFoundError as e:
        return handle_query_data(system.QUERY_EXEC_ERROR, f"发生异常,没有该文件,{e}")
    except Exception as e:
        return handle_query_data(system.QUERY_EXEC_ERROR, f"发生异常,{e}")


def create_files_multi(_file: schemas.multi_file_create, db: Session):
    try:
        error_queue = []
        for f in _file.files:
            file_name = f.split("/")[-1] if len(f.split("/")) > 1 else f.split("\\")[-1]
            file_query_res = db.query(models.file).filter_by(abs_path=f).first()
            if file_query_res:
                error_queue.append(f"文件{file_name}已存在;\n")
                continue
            if os.path.isdir(f):
                file_base_type = "目录"
                file_size = '0'
            else:
                with open(f, "rb") as ff:
                    buffer = ff.read()
                    mime_type = magic.from_buffer(buffer, mime=True)
                file_base_type = mime_to_simple_type.get(mime_type, "未知类型")
                file_size = os.path.getsize(f)
            db_file = models.file(
                file_name=file_name,
                abs_path=f,
                file_base_type=file_base_type,
                file_size=file_size,
                extra=_file.extra
            )
            tag_query_list = []
            for tag in _file.tags:
                tag_query_result = db.query(models.tag).filter_by(id=tag).first()
                if tag_query_result:
                    tag_query_list.append(tag_query_result)
            db_file.tags = tag_query_list
            db.add(db_file)
            db.commit()
        if not error_queue:
            return handle_query_data(system.SUCCESS, "添加成功")
        else:
            return handle_query_data(system.QUERY_BASE_ERROR, "存在问题:".join(error_queue))
    except SQLAlchemyError as e:
        db.rollback()
        return handle_query_data(system.QUERY_EXEC_ERROR, f"在添加数据库时发生异常,{e}")
    except FileNotFoundError as e:
        return handle_query_data(system.QUERY_EXEC_ERROR, f"发生异常,没有该文件,{e}")
    except Exception as e:
        return handle_query_data(system.QUERY_EXEC_ERROR, f"发生异常,{e}")


def get_file_list(db: Session):
    """
    获取所有文件列表
    file_name:str
    abs_path:str
    file_base_type
    """
    db_file_list = db.query(models.file).all()
    data_list = []
    for db_file in db_file_list:
        relate_tag_list = []
        for relate_tag in db_file.tags:
            relate_tag_list.append({
                "id": relate_tag.id,
                "tag_name": relate_tag.tag_name,
            })
        data_list.append({
            "id": db_file.id,
            "file_name": db_file.file_name,
            "abs_path": db_file.abs_path,
            "file_base_type": db_file.file_base_type,
            "create_at": get_datetime_formater(db_file.create_at),
            "extra": db_file.extra,
            "file_size": db_file.get_file_size()[0],
            "file_size_unit": db_file.get_file_size()[1],
            "tags": relate_tag_list
        })
    return handle_query_data(system.SUCCESS, "", data_list)


def delete_file(param1: int, db: Session):
    try:
        db_file_query = db.query(models.file).filter_by(id=param1).first()
        if not db_file_query:
            return handle_query_data(system.QUERY_BASE_ERROR, "对象不存在")
        db.delete(db_file_query)
        db.commit()
        return handle_query_data(system.SUCCESS, "删除成功")
    except SQLAlchemyError as e:
        return handle_query_data(system.QUERY_EXEC_ERROR, f"发生异常,{e}")


def search_tag(param1: Optional[int], db: Session):
    if param1 == -1:
        return get_file_list(db)
    db_tag_query = db.query(models.tag).filter_by(id=param1)
    file_list = []
    file_id_list = []

    def get_tag_file(_db_tag: models.tag):
        for tag_file in _db_tag.files:
            if tag_file.id not in file_id_list:
                relate_tag_list = []
                for relate_tag in tag_file.tags:
                    relate_tag_list.append({
                        "id": relate_tag.id,
                        "tag_name": relate_tag.tag_name,
                    })
                file_list.append({
                    "id": tag_file.id,
                    "file_name": tag_file.file_name,
                    "abs_path": tag_file.abs_path,
                    "file_base_type": tag_file.file_base_type,
                    "create_at": get_datetime_formater(tag_file.create_at),
                    "extra": tag_file.extra,
                    "file_size": tag_file.get_file_size()[0],
                    "file_size_unit": tag_file.get_file_size()[1],
                    "tags": relate_tag_list
                })
                file_id_list.append(tag_file.id)

    # 通过父标签可以找到子标签
    def get_tag_files(_db_tag: models.tag):
        get_tag_file(_db_tag)
        if _db_tag.child_tags:
            for child_tag in _db_tag.child_tags:
                get_tag_files(child_tag)
            return

    for db_tag in db_tag_query:
        get_tag_files(db_tag)
    return handle_query_data(system.SUCCESS, "", file_list)


def update_file_tags(file_tag: schemas.file_tags, db: Session):
    db_file_query = db.query(models.file).filter_by(id=file_tag.file_id).first()
    if db_file_query is not None:
        try:
            file_tag_list = [tag.id for tag in db_file_query.tags]
            if file_tag.direction == 1:
                for tag_id in file_tag.tags_id:
                    if tag_id not in file_tag_list:
                        db_tag_append = db.query(models.tag).filter_by(id=tag_id).first()
                        if db_tag_append:
                            db_file_query.tags.append(db_tag_append)
            else:
                for tag_id in file_tag.tags_id:
                    if tag_id in file_tag_list:
                        db_tag_remove = db.query(models.tag).filter_by(id=tag_id).first()
                        if db_tag_remove:
                            db_file_query.tags.remove(db_tag_remove)
            db.commit()
            return handle_query_data(system.SUCCESS, "更新成功")
        except SQLAlchemyError as e:
            db.rollback()
            return handle_query_data(system.QUERY_EXEC_ERROR, f"发生异常,{e}")
    return handle_query_data(system.QUERY_BASE_ERROR, "文件不存在")


def update_file(_file: schemas.update_file, db: Session):
    db_file_query = db.query(models.file).filter_by(id=_file.id).first()
    if db_file_query is not None:
        try:
            file_tag_list = [tag.id for tag in db_file_query.tags]
            for tag in _file.tags:
                if tag not in file_tag_list:
                    db_tag_append = db.query(models.tag).filter_by(id=tag).first()
                    if db_tag_append:
                        db_file_query.tags.append(db_tag_append)
                else:
                    file_tag_list.remove(tag)
            for tag in file_tag_list:
                db_tag_remove = db.query(models.tag).filter_by(id=tag).first()
                if db_tag_remove:
                    db_file_query.tags.remove(db_tag_remove)
            if _file.file_name:
                db_file_query.file_name = _file.file_name
            db_file_query.extra = _file.extra
            db.commit()
            return handle_query_data(system.SUCCESS, "更新成功")
        except SQLAlchemyError as e:
            db.rollback()
            return handle_query_data(system.QUERY_EXEC_ERROR, f"发生异常,{e}")
    return handle_query_data(system.QUERY_BASE_ERROR, "文件不存在")


def search_file(query: str, db: Session):
    # 文件名 / 标签名 / 类型
    if query == '':
        return get_file_list(db)
    # 构建一个文件id_list
    file_id_list = []
    file_list = []
    db_tag_query = db.query(models.tag).filter(models.tag.tag_name.like(f'%{query}%')).all()
    db_file_query = db.query(models.file).filter(models.file.file_name.like(f'%{query}%')).all()
    db_file_type_query = db.query(models.file).filter(models.file.file_base_type.like(f'%{query}%')).all()
    # 阿巴阿巴
    for f in db_file_query:
        if f.id not in file_id_list:
            relate_tag_list = []
            for relate_tag in f.tags:
                relate_tag_list.append({
                    "id": relate_tag.id,
                    "tag_name": relate_tag.tag_name,
                })
            file_list.append({
                "id": f.id,
                "file_name": f.file_name,
                "abs_path": f.abs_path,
                "file_base_type": f.file_base_type,
                "create_at": get_datetime_formater(f.create_at),
                "extra": f.extra,
                "file_size": f.get_file_size()[0],
                "file_size_unit": f.get_file_size()[1],
                "tags": relate_tag_list
            })
            file_id_list.append(f.id)
    for f in db_file_type_query:
        if f.id not in file_id_list:
            relate_tag_list = []
            for relate_tag in f.tags:
                relate_tag_list.append({
                    "id": relate_tag.id,
                    "tag_name": relate_tag.tag_name,
                })
            file_list.append({
                "id": f.id,
                "file_name": f.file_name,
                "abs_path": f.abs_path,
                "file_base_type": f.file_base_type,
                "create_at": get_datetime_formater(f.create_at),
                "extra": f.extra,
                "file_size": f.get_file_size()[0],
                "file_size_unit": f.get_file_size()[1],
                "tags": relate_tag_list
            })
            file_id_list.append(f.id)
    for t in db_tag_query:
        for f in t.files:
            if f.id not in file_id_list:
                relate_tag_list = []
                for relate_tag in f.tags:
                    relate_tag_list.append({
                        "id": relate_tag.id,
                        "tag_name": relate_tag.tag_name,
                    })
                file_list.append({
                    "id": f.id,
                    "file_name": f.file_name,
                    "abs_path": f.abs_path,
                    "file_base_type": f.file_base_type,
                    "create_at": get_datetime_formater(f.create_at),
                    "extra": f.extra,
                    "file_size": f.get_file_size()[0],
                    "file_size_unit": f.get_file_size()[1],
                    "tags": relate_tag_list
                })
                file_id_list.append(f.id)
    return handle_query_data(system.SUCCESS, "", file_list)

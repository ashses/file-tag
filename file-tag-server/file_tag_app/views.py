from file_tag_app import models, crud, schemas
from utilis.data import handle_return_data
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional, List


def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# tag
def create_tag_view(tag: schemas.tag_create, db: Session = Depends(get_db)):
    if tag.tag_name is not None and tag.extra is not None:
        return handle_return_data("", crud.create_tag(tag=tag, db=db))
    else:
        return handle_return_data("参数错误")


def update_tag_view(tag: schemas.tag_update, db: Session = Depends(get_db)):
    if tag.id:
        return handle_return_data("", crud.update_tag(tag, db))
    else:
        return handle_return_data("需要参数不存在")


def delete_tag_view(tag_id: int, db: Session = Depends(get_db)):
    if tag_id:
        return handle_return_data("", crud.delete_tag(tag_id, db))
    else:
        return handle_return_data("需要参数不存在")


def get_tag_view(db: Session = Depends(get_db)):
    return handle_return_data("", crud.get_tag_list(db))


def create_file_view(file: schemas.file_create, db: Session = Depends(get_db)):
    return handle_return_data("", crud.create_file(_file=file, db=db))


def create_multi_file_view(file: schemas.multi_file_create, db: Session = Depends(get_db)):
    return handle_return_data("", crud.create_files_multi(_file=file, db=db))


def get_file_list_view(db: Session = Depends(get_db)):
    return handle_return_data("", crud.get_file_list(db))


def delete_file_view(file_id: int, db: Session = Depends(get_db)):
    return handle_return_data("", crud.delete_file(file_id, db))


def search_tag_view(tag: Optional[int], db: Session = Depends(get_db)):
    return handle_return_data("", crud.search_tag(tag, db))


def update_file_tags_view(file_tag: schemas.file_tags, db: Session = Depends(get_db)):
    return handle_return_data("", crud.update_file_tags(file_tag, db))


def update_file_view(_file: schemas.update_file, db: Session = Depends(get_db)):
    return handle_return_data("", crud.update_file(_file, db))


def get_a_tag_view(tag_id: Optional[int], db: Session = Depends(get_db)):
    return handle_return_data("", crud.get_a_tag(tag_id, db))


def search_file_view(query: str, db: Session = Depends(get_db)):
    return handle_return_data("", crud.search_file(query, db))

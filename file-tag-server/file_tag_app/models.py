from datetime import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey, String, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from file_tag.config import settings

engine = create_engine(settings.db_url, connect_args=settings.connect_args)
SessionLocal = sessionmaker(autocommit=settings.autocommit,
                            autoflush=settings.autoflush,
                            bind=engine)
Base = declarative_base()

"""
- 标签表
- 文件表

- association:
    - file和file之间是一对多的关系, file可以有parent_file
    - file和tag之间是多对多的关系, file可以有多个tag
    - tag和tag之间是多对多的关系, tag可以有parent_tag
"""

# 关系表
file_tag_association = Table(
    'file_tag_association',
    Base.metadata,
    Column('file_id', Integer, ForeignKey('files.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


# 标签表
class tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(Integer, index=True)
    parent_tag_id = Column(Integer, ForeignKey('tags.id'), nullable=True)
    parent_tag = relationship("tag", remote_side=[id], backref="child_tags")
    # 构建了一个双向引用,会自动生成child_tags属性,例如有: a, b, c三条记录,有关系 (a, b), (a, c),
    # 则可以通过a.child_tags获取到b和c对象,可以通过b.parent_tag和c.parent_tag获取a对象,下面的files同理
    files = relationship("file", secondary=file_tag_association, back_populates="tags")
    create_time = Column(DateTime, default=datetime.utcnow)
    extra = Column(String, nullable=True)


# 文件表
class file(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    abs_path = Column(String)
    file_base_type = Column(String, index=True)
    tags = relationship("tag", secondary=file_tag_association, back_populates="files")
    create_at = Column(DateTime, default=datetime.utcnow)
    extra = Column(String, nullable=True)
    file_size = Column(String)

    def get_file_size(self):
        # 将文件大小转化为（B, KB, MB, GB, TB）
        _file_unit_tag_list = ["B", "KB", "MB", "GB", "TB"]
        _file_size = float(self.file_size)
        _file_unit_tag = _file_unit_tag_list[0]
        index = 1
        while True:
            if _file_size >= 1024:
                _file_size /= 1024
                _file_unit_tag = _file_unit_tag_list[index]
                index += 1
            else:
                break

        return _file_size, _file_unit_tag

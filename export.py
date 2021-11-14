# from typing import Text
# import sqlalchemy
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import Column, Integer, String


# engine = create_engine('sqlite:///info.db')
# if not engine.dialect.has_table(engine, 'datas'):
#     metadata = sqlalchemy.schema.MetaData(engine)
#     sqlalchemy.schema.Table('datas', metadata,
#                             Column('post_id', Integer, primary_key=True, autoincrement=True),
#                             Column('url', String(256)),
#                             # Column('id_', Integer),
#                             Column('author_name', Integer),
#                             Column('post_time', String(256)),
#                             Column('content', Text),
#                             Column('like_num', Integer)
# 	)
#     metadata.create_all()
# Session = sessionmaker(bind=engine)
# session = Session()
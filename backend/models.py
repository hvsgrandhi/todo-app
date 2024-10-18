from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class ToDoItem(Base):
    __tablename__ = 'todo_items'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(250))
    time = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String(250), nullable=True)
    user_id = Column(String(50))

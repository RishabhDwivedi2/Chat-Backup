# [AI]: This file implements the Entry model for the application.
# It provides functionality to represent and manipulate entry data in the database.
# Key features:
# - Defines the structure of the 'entries' table
# - Implements a method to get the timestamp in IST (Indian Standard Time)
# - Provides a string representation of the Entry object

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base  # Change this line
import pytz  # [AI]: Import pytz for timezone handling

# [AI]: Define the Entry model, which represents a single entry in the application
class Entry(Base):
    __tablename__ = 'entries'

    # [AI]: Define the columns of the 'entries' table
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    # [AI]: Use server_default to automatically set the timestamp when an entry is created
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # [AI]: Method to convert the timestamp to Indian Standard Time (IST)
    def get_ist_timestamp(self):
        if self.timestamp:
            # [AI]: Convert the timestamp to IST and format it as a string
            return self.timestamp.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %I:%M:%S %p')
        return None

    # [AI]: Provide a string representation of the Entry object
    def __repr__(self):
        return f"<Entry(id={self.id}, content='{self.content}', timestamp='{self.get_ist_timestamp()}'>"
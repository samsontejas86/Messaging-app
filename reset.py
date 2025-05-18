from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from models import Message

# Connect to the database
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
session = Session()

# Update all messages to have a "new" status
session.query(Message).update({Message.status: "new"})
session.commit()

print("All messages have been reset to 'new' status.")

# Close the session
session.close()

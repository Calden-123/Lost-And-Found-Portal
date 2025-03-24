from LostAndFound import create_app
from LostAndFound.models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # To get the list of tables
    result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    print("Tables in database:")
    for table in result:
        print(table[0])

    # To view data from a specific table (e.g., LostItems)
    #result_data = db.session.execute(text("SELECT * FROM Item;")).fetchall()
    #print("\nData from LostItems table:")
    #for row in result_data:
     #   print(row)

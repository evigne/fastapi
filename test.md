In SQLAlchemy, when dealing with a one-to-many relationship between TableA and TableB, you can insert records into both tables efficiently using SQLAlchemy ORM.

Example: One-to-Many Relationship in SQLAlchemy

Schema Definition


from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session, declarative_base

Base = declarative_base()

class TableA(Base):
    __tablename__ = "table_a"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Define one-to-many relationship
    tablebs = relationship("TableB", back_populates="parent", cascade="all, delete-orphan")

class TableB(Base):
    __tablename__ = "table_b"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_a_id = Column(Integer, ForeignKey("table_a.id"), nullable=False)
    value = Column(String, nullable=False)

    # Define back-reference to TableA
    parent = relationship("TableA", back_populates="tablebs")

# Create an SQLite in-memory database for testing
engine = create_engine("sqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)

Insert Data with Relationship

When inserting TableA along with its related TableB records, you can use SQLAlchemy ORM’s relationship handling.

# Open a session
with Session(engine) as session:
    # Create TableA instance with related TableB instances
    new_a = TableA(
        name="Parent Record",
        tablebs=[
            TableB(value="Child Record 1"),
            TableB(value="Child Record 2"),
        ]
    )

    # Add and commit
    session.add(new_a)
    session.commit()

    # Verify insertion
    for b in new_a.tablebs:
        print(f"TableB ID: {b.id}, Value: {b.value}")

How It Works
	1.	When creating a TableA record, we pass a list of TableB instances in the tablebs relationship.
	2.	Since we set cascade="all, delete-orphan", adding a TableA object automatically takes care of the related TableB records.
	3.	session.add(new_a) adds everything in one go.
	4.	session.commit() persists all changes to the database.

Alternative: Insert Separately

If you already have a TableA record and want to insert TableB records later:

with Session(engine) as session:
    parent = session.query(TableA).filter_by(name="Parent Record").first()
    
    new_b = TableB(value="New Child", parent=parent)
    session.add(new_b)
    session.commit()

This approach is useful if TableA already exists and you need to add new TableB records dynamically.








######
To perform an upsert (insert new or update existing) operation for related TableB records in SQLAlchemy, you can use SQLAlchemy ORM merge strategies or custom update logic.

Approach 1: Using merge() (Recommended for Upserts)

The session.merge() method will:
	•	Insert new records if they don’t exist.
	•	Update existing records if they already exist.

Modified Code with Upsert Logic

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session, declarative_base

Base = declarative_base()

class TableA(Base):
    __tablename__ = "table_a"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Define one-to-many relationship
    tablebs = relationship("TableB", back_populates="parent", cascade="all, delete-orphan")

class TableB(Base):
    __tablename__ = "table_b"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_a_id = Column(Integer, ForeignKey("table_a.id"), nullable=False)
    value = Column(String, nullable=False)

    parent = relationship("TableA", back_populates="tablebs")

# Create an SQLite in-memory database
engine = create_engine("sqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)

Performing Upsert (Insert or Update)

def upsert_tablea_with_tablebs(session, name, tableb_data):
    """
    Upsert TableA and its related TableB records.

    :param session: SQLAlchemy session
    :param name: Name of TableA
    :param tableb_data: List of dictionaries containing TableB data
    """
    # Try to find existing TableA record
    tablea = session.query(TableA).filter_by(name=name).first()

    if tablea is None:
        # If TableA does not exist, create it
        tablea = TableA(name=name)

    # Track existing TableB records by ID
    existing_b_map = {b.id: b for b in tablea.tablebs}

    # Upsert TableB records
    for b_data in tableb_data:
        b_id = b_data.get("id")  # ID may be provided for updates

        if b_id and b_id in existing_b_map:
            # Update existing TableB record
            existing_b_map[b_id].value = b_data["value"]
        else:
            # Insert new TableB record
            new_b = TableB(value=b_data["value"], parent=tablea)
            session.add(new_b)

    # Save changes
    session.add(tablea)
    session.commit()

# Example usage
with Session(engine) as session:
    # First insert (new records)
    upsert_tablea_with_tablebs(session, "Parent Record", [
        {"value": "Child 1"},
        {"value": "Child 2"}
    ])

    # Second upsert (update Child 1, insert new Child 3)
    upsert_tablea_with_tablebs(session, "Parent Record", [
        {"id": 1, "value": "Updated Child 1"},  # Existing record, updated
        {"value": "Child 3"}  # New record
    ])

How It Works
	1.	Find existing TableA: If it exists, use it; otherwise, create it.
	2.	Map existing TableB records by ID to detect updates.
	3.	Iterate through tableb_data:
	•	If an ID exists and matches, update the record.
	•	Otherwise, insert a new record.
	4.	Commit all changes in a single transaction.

Alternative: Using session.merge()

If you prefer merge() (simpler but less control over updates):

with Session(engine) as session:
    tablea = session.merge(TableA(
        name="Parent Record",
        tablebs=[
            TableB(id=1, value="Updated Child 1"),  # Update existing
            TableB(value="Child 3")  # Insert new
        ]
    ))
    session.commit()

Final Thoughts
	•	If you want more control over updates and inserts, use explicit queries (query().filter()).
	•	If you want a simpler solution and are okay with potential inefficiencies, use session.merge().

Would you like to refine this further based on your exact use case?


Would you like help adapting this to your specific use case?
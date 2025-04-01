import json
from sqlalchemy import create_engine, Column, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the database connection
DATABASE_URL = "postgresql://fouxan:fouxanpsql@localhost:5432/ripd"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Define the Base
Base = declarative_base()


# Define the Table
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    force = Column(Text, nullable=False)
    level = Column(Text, nullable=False)
    mechanic = Column(Text, nullable=False)
    equipment = Column(Text, nullable=False)
    primary_muscles = Column(JSONB, nullable=False)
    secondary_muscles = Column(JSONB, nullable=False)
    instructions = Column(JSONB, nullable=False)
    category = Column(Text, nullable=False)
    images = Column(JSONB, nullable=False)


# Function to load data from JSON and insert into DB
def import_json_to_db(json_file, image_prefix):
    # Create table if it doesn't exist
    Base.metadata.create_all(engine)

    # Open a session
    session = SessionLocal()

    # Load JSON data
    with open(json_file, "r", encoding="utf-8") as file:
        exercises = json.load(file)

    # Transform and insert data
    for exercise in exercises:
        exercise["images"] = [
            image_prefix + img for img in exercise["images"]
        ]  # Add prefix to images

        new_exercise = Activity(
            id=exercise["id"],
            name=exercise["name"],
            force=exercise["force"],
            level=exercise["level"],
            mechanic=exercise["mechanic"],
            equipment=exercise["equipment"],
            primary_muscles=exercise["primaryMuscles"],  # Stored as JSONB
            secondary_muscles=exercise["secondaryMuscles"],  # Stored as JSONB
            instructions=exercise["instructions"],  # Stored as JSONB
            category=exercise["category"],
            images=exercise["images"],  # Stored as JSONB
        )

        session.add(new_exercise)

    # Commit and close session
    session.commit()
    session.close()
    print("Data imported successfully!")


# Usage
if __name__ == "__main__":
    json_file_path = "./data/exercises.json"  # Replace with your JSON file path
    image_prefix = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises/"  # Example prefix
    import_json_to_db(json_file_path, image_prefix)

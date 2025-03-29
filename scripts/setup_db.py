from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Define the database (SQLite)
DATABASE_URL = "sqlite:///fitness.db"  # Database file will be created in the current directory
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=True to see SQL queries

# Base class for ORM models
Base = declarative_base()

# Define the association table for many-to-many relationship (if needed)
# activity_item_association = Table(
#     "activity_item_association",
#     Base.metadata,
#     Column("activity_id", Integer, ForeignKey("activities.id")),
#     Column("item_id", Integer, ForeignKey("items.id")),
# )

# Define the Category model
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    items = relationship("Item", back_populates="category")

# Define the Item model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    url = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="items")
    activity_ids = Column(String)  # Store as a comma-separated string or JSON
    links = Column(String)  # Store as a comma-separated string or JSON

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

data = {
  "categories": [
    {
      "category": "Body Part",
      "description": "Exercises categorized by the muscle group or body part they target.",
      "items": [
        {
          "name": "Abs",
          "description": "Exercises targeting the abdominal muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/abs"
        },
        {
          "name": "Adductors",
          "description": "Exercises targeting the inner thigh muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/adductors.html"
        },
        {
          "name": "Biceps",
          "description": "Exercises targeting the bicep muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/biceps"
        },
        {
          "name": "Calves",
          "description": "Exercises targeting the calf muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/calves"
        },
        {
          "name": "Chest",
          "description": "Exercises targeting the chest muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/chest"
        },
        {
          "name": "Forearms",
          "description": "Exercises targeting the forearm muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/forearms"
        },
        {
          "name": "Glutes",
          "description": "Exercises targeting the gluteal muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/glutes"
        },
        {
          "name": "Hamstrings",
          "description": "Exercises targeting the hamstring muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/hamstrings"
        },
        {
          "name": "Hip Flexors",
          "description": "Exercises targeting the hip flexor muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/hip-flexors"
        },
        {
          "name": "IT Band",
          "description": "Exercises targeting the iliotibial band.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/it-band"
        },
        {
          "name": "Lats",
          "description": "Exercises targeting the latissimus dorsi muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/lats"
        },
        {
          "name": "Lower Back",
          "description": "Exercises targeting the lower back muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/lower-back"
        },
        {
          "name": "Middle Back",
          "description": "Exercises targeting the middle back muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/middle-back"
        },
        {
          "name": "Neck",
          "description": "Exercises targeting the neck muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/neck.html"
        },
        {
          "name": "Obliques",
          "description": "Exercises targeting the oblique muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/obliques"
        },
        {
          "name": "Palmar Fascia",
          "description": "Exercises targeting the palmar fascia.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/palmar-fascia"
        },
        {
          "name": "Plantar Fascia",
          "description": "Exercises targeting the plantar fascia.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/plantar-fascia"
        },
        {
          "name": "Quads",
          "description": "Exercises targeting the quadriceps muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/quads"
        },
        {
          "name": "Shoulders",
          "description": "Exercises targeting the shoulder muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/shoulders"
        },
        {
          "name": "Traps",
          "description": "Exercises targeting the trapezius muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/traps"
        },
        {
          "name": "Triceps",
          "description": "Exercises targeting the tricep muscles.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/triceps"
        }
      ]
    },
    {
      "category": "Equipment",
      "description": "Exercises categorized by the equipment required to perform them.",
      "items": [
        {
          "name": "Dumbbell",
          "description": "Exercises performed using dumbbells.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/dumbbell"
        },
        {
          "name": "Barbell",
          "description": "Exercises performed using a barbell.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/barbell"
        },
        {
          "name": "Bodyweight",
          "description": "Exercises performed using only body weight.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/bodyweight"
        },
        {
          "name": "Cable",
          "description": "Exercises performed using a cable machine.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/cable"
        },
        {
          "name": "Machine",
          "description": "Exercises performed using gym machines.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/machine"
        },
        {
          "name": "Exercise Ball",
          "description": "Exercises performed using an exercise ball.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/exercise-ball"
        },
        {
          "name": "EZ Bar",
          "description": "Exercises performed using an EZ bar.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/ez-bar"
        }
      ]
    },
    {
      "category": "Mechanic",
      "description": "Exercises categorized by their movement type (compound or isolation).",
      "items": [
        {
          "name": "Compound",
          "description": "Exercises that engage multiple muscle groups.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/compound"
        },
        {
          "name": "Isolation",
          "description": "Exercises that target a single muscle group.",
          "activity_ids": [],
          "links": [],
          "url": "https://www.muscleandstrength.com/exercises/isolation"
        }
      ]
    }
  ]
}

# Insert data into the database
for category_data in data["categories"]:
    category = Category(
        name=category_data["category"],
        description=category_data["description"]
    )
    session.add(category)
    session.commit()  # Commit to get the category ID

    for item_data in category_data["items"]:
        item = Item(
            name=item_data["name"],
            description=item_data["description"],
            url=item_data["url"],
            activity_ids=str(item_data["activity_ids"]),  # Convert list to string
            links=str(item_data["links"]),  # Convert list to string
            category_id=category.id
        )
        session.add(item)

# Commit the transaction
session.commit()

# Close the session
session.close()

print("Database setup and data insertion complete!")
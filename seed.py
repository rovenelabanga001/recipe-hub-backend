import os
import random
import io
from faker import Faker
from mongoengine import connect, get_db
from models.user import User
from models.recipe import Recipe
from models.comment import Comment
from models.notification import Notification
from PIL import Image
from bson.errors import InvalidId
from gridfs.errors import NoFile

# --- Database Connection ---
# Make sure this matches your Flask app's connection string
connect("recipehub", host="mongodb://localhost:27017")
print("Connected to MongoDB.")

# --- Data Cleanup ---
try:
    db = get_db()
    db.drop_collection("user")
    db.drop_collection("recipe")
    db.drop_collection("comment")
    db.drop_collection("notification")
    # GridFS collections are named 'fs.files' and 'fs.chunks' by default
    db.drop_collection("fs.files")
    db.drop_collection("fs.chunks")
    print("Dropped existing collections, including GridFS.")
except Exception as e:
    print(f"Error dropping collections: {e}")

fake = Faker()
CATEGORIES = ["breakfast", "brunch", "lunch", "dinner", "dessert", "snack"]

def create_dummy_image():
    """Generates a simple dummy image for recipe seeding."""
    img = Image.new("RGB", (800, 600), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    return img_byte_arr

# --- Seed Users ---
print("Seeding 5 users...")
users = []
try:
    for _ in range(5):
        user = User.create(
            email=fake.unique.email(),
            username=fake.unique.user_name(),
            password="password123"
        )
        users.append(user)
    print(f"Seeded {len(users)} users.")
except Exception as e:
    print(f"Error seeding users: {e}")
    exit()

# --- Seed Recipes ---
print("Seeding 20 recipes...")
recipes = []
for i in range(20):
    user = random.choice(users)
    try:
        recipe = Recipe(
            name=fake.catch_phrase(),
            title=fake.sentence(nb_words=6),
            prepTime=random.randint(5, 30),
            cookTime=random.randint(10, 60),
            servings=random.randint(1, 8),
            ingredients=[fake.word() for _ in range(random.randint(3, 7))],
            directions=[fake.sentence() for _ in range(random.randint(5, 10))],
            tags=[fake.word() for _ in range(random.randint(2, 5))],
            category=[random.choice(CATEGORIES)],
            user=user,
        )
        
        # Create and put the image data into the ImageField.
        img_stream = create_dummy_image()
        recipe.image.put(img_stream, content_type="image/jpeg")

        # Save the document. This is when the GridFS write is finalized.
        recipe.save()
        recipes.append(recipe)
        print(f"✅ Recipe {recipe.id} created with GridFS ID: {recipe.image.grid_id}")
    except Exception as e:
        print(f"❌ Error seeding recipe {i+1}: {e}")

print(f"Seeded {len(recipes)} recipes.")

# --- Seed Comments ---
print("Seeding 10 comments...")
comments = []
if recipes: # Ensure there are recipes to comment on
    for i in range(10):
        try:
            user = random.choice(users)
            recipe = random.choice(recipes)
            comment = Comment(
                user=user,
                recipe=recipe,
                body=fake.paragraph(nb_sentences=2)
            )
            comment.save()
            comments.append(comment)
        except Exception as e:
            print(f"❌ Error seeding comment {i+1}: {e}")
print(f"Seeded {len(comments)} comments.")

# --- Verification ---
print("\nVerification:")
print(f"Total Users: {User.objects.count()}")
print(f"Total Recipes: {len(recipes)}")
print(f"Total Comments: {len(comments)}")
print(f"Total Notifications: {Notification.objects.count()}")
try:
    db = get_db()
    print(f"Total GridFS Files: {db.fs.files.count_documents({})}")
    print(f"Total GridFS Chunks: {db.fs.chunks.count_documents({})}")
except Exception as e:
    print(f"Error during verification: {e}")

print("\nSeeding complete!")
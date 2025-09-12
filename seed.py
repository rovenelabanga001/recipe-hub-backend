# seed.py
import datetime
from mongoengine import connect
from models.user import User
from models.recipe import Recipe
from models.comment import Comment
from models.notification import Notification

# ----------------------
# Connect to MongoDB
# ----------------------
connect(db="recipehub", host="mongodb://localhost:27017/recipehub")

def seed():
    # ----------------------
    # Clear existing collections
    # ----------------------
    User.drop_collection()
    Recipe.drop_collection()
    Comment.drop_collection()
    Notification.drop_collection()
    print("🗑 Cleared existing collections...")

    # ----------------------
    # 1️⃣ Create Users
    # ----------------------
    user1 = User.create(
        email="john@example.com",
        username="john_doe",
        password="password123"
    )

    user2 = User.create(
        email="sara@example.com",
        username="sara_smith",
        password="password456"
    )

    print(f"✅ Created users: {user1.username}, {user2.username}")

    # ----------------------
    # 2️⃣ Create Recipes
    # ----------------------
    recipe1 = Recipe(
        name="Classic Beef Steak",
        image=None,
        title="Juicy Grilled Steak",
        prepTime=20,
        cookTime=15,
        servings=2,
        ingredients=["2 Beef steaks", "Salt", "Pepper", "Garlic butter"],
        directions=[
            "Season steak with salt and pepper.",
            "Preheat grill to medium-high heat.",
            "Grill steaks for 6–8 minutes per side for medium doneness.",
            "Top with garlic butter before serving."
        ],
        tags=["main course", "grilled", "beef"],
        category=["Lunch", "Dinner"],
        user=user1
    ).save()

    recipe2 = Recipe(
        name="Banana Pancakes",
        image=None,
        title="Fluffy Banana Pancakes",
        prepTime=10,
        cookTime=10,
        servings=4,
        ingredients=["2 Bananas", "1 cup Flour", "1 Egg", "Milk", "Baking powder"],
        directions=[
            "Mash bananas in a bowl.",
            "Mix with egg, flour, and milk until smooth.",
            "Cook pancakes on a non-stick pan.",
            "Serve with honey or syrup."
        ],
        tags=["breakfast", "sweet", "vegetarian"],
        category=["Breakfast"],
        user=user2
    ).save()

    print(f"✅ Created recipes: {recipe1.title}, {recipe2.title}")

    # ----------------------
    # 3️⃣ Update users’ favoriteRecipeIds
    # ----------------------
    user1.favoriteRecipeIds = [recipe2.id]  # John likes Banana Pancakes
    user1.save()
    user2.favoriteRecipeIds = [recipe1.id]  # Sara likes Beef Steak
    user2.save()
    print("⭐ Updated users' favorite recipes")

    # ----------------------
    # 4️⃣ Create Comments
    # ----------------------
    comment1 = Comment(
        user=user2,  # reference user object
        recipe=recipe1,
        body="Loved the flavors, but I added a bit more spice to suit my taste.",
        time=datetime.datetime(2025, 8, 22, 7, 45)
    ).save()

    comment2 = Comment(
        user=user1,
        recipe=recipe2,
        body="These pancakes were fluffy and delicious!",
        time=datetime.datetime(2025, 9, 1, 10, 30)
    ).save()

    print("💬 Created comments")

    # ----------------------
    # 5️⃣ Create Notifications
    # ----------------------
    Notification(
        user=user1,
        type="favorite",
        actor=user2,
        message=f"{user2.username} liked your recipe \"{recipe2.name}\"",
        recipe=recipe2,
        createdAt=datetime.datetime.utcnow(),
        read=False
    ).save()

    Notification(
        user=user2,
        type="comment",
        actor=user1,
        message=f"{user1.username} commented on your recipe \"{recipe2.name}\"",
        recipe=recipe2,
        createdAt=datetime.datetime.utcnow(),
        read=False,
        comment=comment2
    ).save()

    print("🔔 Created notifications")
    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed()

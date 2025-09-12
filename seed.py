# seed.py
import datetime
from mongoengine import connect
from models.user import User
from models.recipe import Recipe
from models.comment import Comment
from models.notification import Notification

# Connect to DB
connect(
    db="recipehub",
    host="mongodb://localhost:27017/recipehub"
)

def seed():
    # Clear existing collections (optional, helpful in dev)
    User.drop_collection()
    Recipe.drop_collection()
    Comment.drop_collection()
    Notification.drop_collection()

    # ----------------------
    # Create Recipes first
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
        userId=None  # will update later
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
        userId=None
    ).save()

    # ----------------------
    # Create Users with favoriteRecipeIds pointing to existing recipes
    # ----------------------
    user1 = User.create(
        email="john@example.com",
        username="john_doe",
        password="password123",
        favoriteRecipeIds=[recipe2.id]  # John likes Banana Pancakes
    )

    user2 = User.create(
        email="sara@example.com",
        username="sara_smith",
        password="password456",
        favoriteRecipeIds=[recipe1.id]  # Sara likes Beef Steak
    )

    # Now that users exist, update recipes with their owners
    recipe1.userId = user1.id
    recipe1.save()
    recipe2.userId = user2.id
    recipe2.save()

    # ----------------------
    # Create Comments
    # ----------------------
    comment1 = Comment(
        username=user2.username,
        recipeId=recipe1.id,
        body="Loved the flavors, but I added a bit more spice to suit my taste.",
        time=datetime.datetime(2025, 8, 22, 7, 45)
    ).save()

    comment2 = Comment(
        username=user1.username,
        recipeId=recipe2.id,
        body="These pancakes were fluffy and delicious!",
        time=datetime.datetime(2025, 9, 1, 10, 30)
    ).save()

    # ----------------------
    # Create Notifications
    # ----------------------
    Notification(
        userId=user1.id,
        type="favorite",
        user=user2.username,
        message=f"{user2.username} liked your recipe \"{recipe2.name}\"",
        recipeId=recipe2.id,
        createdAt=datetime.datetime.utcnow(),
        read=False
    ).save()

    Notification(
        userId=user2.id,
        type="comment",
        user=user1.username,
        message=f"{user1.username} commented on your recipe \"{recipe2.name}\"",
        recipeId=recipe2.id,
        createdAt=datetime.datetime.utcnow(),
        read=False,
        commentId=comment2.id
    ).save()

    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed()

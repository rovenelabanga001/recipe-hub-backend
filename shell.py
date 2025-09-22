from models.recipe import Recipe
from models.user import User
from mongoengine import connect
connect(
    db="recipehub",
    host="mongodb://localhost:27017/recipehub"
)
# Copy favoriteCount → likeCount for all documents
for recipe in Recipe.objects():
    if hasattr(recipe, "favoriteCount"):
        recipe.likeCount = recipe.favoriteCount
        recipe.save()

# Optionally remove old field (if you want a clean schema)
Recipe.objects().update(unset__favoriteCount=1)

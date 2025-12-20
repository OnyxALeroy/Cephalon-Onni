import asyncio
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from database.dynamic.security import hash_password
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["cephalon_onni"]
users_collection = db["users"]


async def list_all_users():
    """List all users in the system"""
    print("\n=== All Users ===")
    users = []
    cursor = users_collection.find({})

    async for user in cursor:
        users.append(
            {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "role": user.get("role", "Tenno"),
            }
        )

    if not users:
        print("No users found.")
        return

    for user in users:
        print(f"ID: {user['id']}")
        print(f"Email: {user['email']}")
        print(f"Username: {user['username']}")
        print(f"Role: {user['role']}")
        print("-" * 40)


async def update_user_role(user_id: str, new_role: str):
    """Update a user's role"""
    valid_roles = ["Traveller", "Tenno", "Administrator"]

    if new_role not in valid_roles:
        print(f"Invalid role. Valid roles: {', '.join(valid_roles)}")
        return

    try:
        from bson import ObjectId

        object_id = ObjectId(user_id)
    except Exception as e:
        print(f"Invalid user ID format: {e}")
        return

    result = await users_collection.update_one(
        {"_id": object_id}, {"$set": {"role": new_role}}
    )

    if result.modified_count > 0:
        print(f"Successfully updated user role to {new_role}")
    else:
        print("User not found or role unchanged")


async def create_admin_user(email: str, username: str, password: str):
    """Create a new administrator user"""
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": email})
    if existing_user:
        print("User with this email already exists")
        return

    # Create new admin user
    admin_user = {
        "email": email,
        "username": username,
        "hashed_password": hash_password(password),
        "role": "Administrator",
    }

    result = await users_collection.insert_one(admin_user)

    print("Administrator user created successfully!")
    print(f"ID: {result.inserted_id}")
    print(f"Email: {email}")
    print(f"Username: {username}")
    print("Role: Administrator")


async def delete_user(user_id: str):
    """Delete a user from the system"""
    try:
        from bson import ObjectId

        object_id = ObjectId(user_id)
    except Exception as e:
        print(f"Invalid user ID format: {e}")
        return

    # Get user info before deletion
    user = await users_collection.find_one({"_id": object_id})
    if not user:
        print("User not found")
        return

    if user.get("role") == "Administrator":
        confirm = input(
            "This is an Administrator user. Are you sure you want to delete? (y/N): "
        )
        if confirm.lower() != "y":
            print("Operation cancelled")
            return

    result = await users_collection.delete_one({"_id": object_id})
    if result.deleted_count > 0:
        print(f"User '{user.get('username', 'Unknown')}' deleted successfully")
    else:
        print("User not found")


def show_help():
    """Display available commands"""
    print("\nAvailable operations:")
    print("1. List all users")
    print("2. Update user role")
    print("3. Create administrator")
    print("4. Delete user")
    print("5. Exit")


async def main():
    print("Cephalon Onni - Role Management Tool")
    print("=" * 50)
    show_help()

    while True:
        print("\n" + "=" * 50)
        choice = input("\n> ").strip()

        if choice == "1":
            await list_all_users()

        elif choice == "2":
            user_id = input("Enter user ID: ").strip()
            new_role = input("Enter new role (Traveller/Tenno/Administrator): ").strip()
            await update_user_role(user_id, new_role)

        elif choice == "3":
            email = input("Enter email: ").strip()
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            await create_admin_user(email, username, password)

        elif choice == "4":
            user_id = input("Enter user ID to delete: ").strip()
            await delete_user(user_id)

        elif choice == "5" or choice.lower() in ["exit", "quit"]:
            print("Exiting role management tool")
            break

        elif choice.lower() == "help":
            show_help()

        else:
            print("Invalid choice.")
            show_help()


if __name__ == "__main__":
    asyncio.run(main())

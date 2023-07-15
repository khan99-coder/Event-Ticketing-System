from enum import Enum
import json

# Define the UserRole enum
class UserRole(Enum):
    USER = 1
    ADMIN = 2

# Load the admin usernames or user IDs from a configuration file
with open('admin_config.json') as config_file:
    admin_config = json.load(config_file)
    admin_usernames = admin_config.get('usernames', [])
    admin_user_ids = admin_config.get('user_ids', [])

# Assuming you have a User class similar to the previous example
class User:
    def __init__(self, name, username, user_id):
        self.name = name
        self.username = username
        self.user_id = user_id
        self.role = UserRole.ADMIN if self.is_admin() else UserRole.USER

    def is_admin(self):
        return self.username in admin_usernames or self.user_id in admin_user_ids

# Example usage:
user1 = User("John Doe", "johndoe", 1234)
user2 = User("Paul", "popo", 456)

print(user1.name, user1.role) 
print(user2.name, user2.role)  

# frontend/app_state.py

class AppState:
    """
    Singleton to store app-wide state, including cart and current user.
    """
    _instance = None

    def __init__(self):
        self.cart = {}  # {book_id: {"title": str, "price": float, "quantity": int}}
        self.current_user = None  # Staff or Customer dict

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
# frontend/app_state.py

class AppState:
    """
    Singleton to store app-wide state, including cart and current user.
    """
    _instance = None

    def __init__(self):
        self.cart = {}  # {book_id: {"title": str, "price": float, "quantity": int}}
        self.current_user = None  # Staff or Customer dict

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

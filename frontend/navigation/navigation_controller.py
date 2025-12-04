# frontend/navigation/navigation_controller.py

import tkinter as tk

from frontend.views.login_view import LoginView
from frontend.views.home_search_view import HomeSearchView
from frontend.views.profile_view import ProfileView
from frontend.views.reports_view import ReportsView
# Additional views can be added later


class NavigationController:
    """
    Manages transitions between screens.
    Ensures only 1 screen is visible at a time.
    Stores session info (logged-in user).
    """

    def __init__(self, root):
        self.root = root
        self.current_screen = None

        # Session storage
        self.user = None          # dict: user_id, role, username, etc.

        # Start with login screen
        self.show_login()

    # -----------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------
    def _clear_screen(self):
        """Hides and destroys the currently shown screen."""
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

    def _swap(self, new_screen):
        """Replace the displayed screen."""
        self._clear_screen()
        self.current_screen = new_screen
        self.current_screen.grid(row=0, column=0, sticky="nsew")

    # -----------------------------------------------------------
    # Screens
    # -----------------------------------------------------------

    def show_login(self):
        screen = LoginView(
            self.root,
            self.login_success
        )
        self._swap(screen)

    def login_success(self, user_object):
        """
        Called from LoginView when authentication succeeds.
        user_object contains: user_id, username, role, privileges...
        """
        self.user = user_object
        self.show_home()

    def logout(self):
        self.user = None
        self.show_login()

    def show_home(self):
        screen = HomeSearchView(
            root=self.root,
            user_role=self.user["role"],
            username=self.user["username"]
        )
        # Home needs to call navigation (side menu buttons)
        screen.switch_page = self.navigate_from_home
        self._swap(screen)

    # -----------------------------------------------------------
    # Routes FROM the home page
    # -----------------------------------------------------------
    def navigate_from_home(self, page_id):
        """
        Called when the user clicks items in the side menu.
        """
        if page_id == "home":
            self.show_home()
        elif page_id == "profile":
            self.show_profile()
        elif page_id == "reports":
            self.show_reports()
        elif page_id == "logout":
            self.logout()
        elif page_id == "books":
            from frontend.views.admin.manage_books_view import ManageBooksView
            screen = ManageBooksView(self.root, go_back=self.show_home)
            self._swap(screen)
        elif page_id == "authors":
            from frontend.views.admin.manage_authors_view import ManageAuthorsView
            screen = ManageAuthorsView(self.root, go_back=self.show_home)
            self._swap(screen)
        elif page_id == "publishers":
            from frontend.views.admin.manage_publishers_view import ManagePublishersView
            screen = ManagePublishersView(self.root, go_back=self.show_home)
            self._swap(screen)
        elif page_id == "categories":
            from frontend.views.admin.manage_categories_view import ManageCategoriesView
            screen = ManageCategoriesView(self.root, go_back=self.show_home)
            self._swap(screen)
        elif page_id == "customers":
            from frontend.views.admin.manage_customers_view import ManageCustomersView
            screen = ManageCustomersView(self.root, go_back=self.show_home)
            self._swap(screen)
        elif page_id == "staff":
            from frontend.views.admin.manage_staff_view import ManageStaffView
            screen = ManageStaffView(self.root, go_back=self.show_home)
            self._swap(screen)
        elif page_id == "inventory" or page_id == "inventory_mgmt":
            from frontend.views.admin.manage_inventory_view import ManageInventoryView
            screen = ManageInventoryView(self.root, go_back=self.show_home)
            self._swap(screen)


        else:
            print("Unknown page:", page_id)

    # -----------------------------------------------------------
    # Staff/Admin pages
    # -----------------------------------------------------------
    def show_profile(self):
        screen = ProfileView(
            self.root,
            user=self.user,
            go_back=self.show_home
        )
        self._swap(screen)

    def show_reports(self):
        screen = ReportsView(
            self.root,
            user_role=self.user["role"],
            go_back=self.show_home
        )
        self._swap(screen)

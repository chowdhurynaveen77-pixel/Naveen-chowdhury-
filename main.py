from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import json
import os

PRODUCT_FILE = "products.json"
ORDER_FILE = "orders.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.username = TextInput(hint_text="Username", size_hint_y=None, height=50)
        self.password = TextInput(hint_text="Password", password=True, size_hint_y=None, height=50)
        login_btn = Button(text="Login", size_hint_y=None, height=50)
        self.message = Label(text="")

        login_btn.bind(on_press=self.check_login)

        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_btn)
        layout.add_widget(self.message)

        self.add_widget(layout)

    def check_login(self, instance):
        if self.username.text == "admin" and self.password.text == "1234":
            self.manager.current = "admin"
        elif self.username.text == "user" and self.password.text == "1111":
            self.manager.current = "chat"
        else:
            self.message.text = "Wrong Login ❌"

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.product_name = TextInput(hint_text="Product Name", size_hint_y=None, height=50)
        self.product_price = TextInput(hint_text="Product Price", size_hint_y=None, height=50)

        add_btn = Button(text="Add Product", size_hint_y=None, height=50)
        view_sales_btn = Button(text="View Sales", size_hint_y=None, height=50)
        back_btn = Button(text="Logout", size_hint_y=None, height=50)

        self.message = Label(text="")

        add_btn.bind(on_press=self.add_product)
        view_sales_btn.bind(on_press=self.view_sales)
        back_btn.bind(on_press=self.logout)

        layout.add_widget(self.product_name)
        layout.add_widget(self.product_price)
        layout.add_widget(add_btn)
        layout.add_widget(view_sales_btn)
        layout.add_widget(self.message)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def add_product(self, instance):
        name = self.product_name.text.lower()
        price = self.product_price.text

        products = load_json(PRODUCT_FILE)
        products[name] = price
        save_json(PRODUCT_FILE, products)

        self.message.text = "Product Added ✅"
        self.product_name.text = ""
        self.product_price.text = ""

    def view_sales(self, instance):
        orders = load_json(ORDER_FILE)
        total = sum(int(price) for price in orders.values()) if orders else 0
        self.message.text = f"Total Orders: {len(orders)} | Total ₹{total}"

    def logout(self, instance):
        self.manager.current = "login"

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.scroll = ScrollView()
        self.chat_layout = GridLayout(cols=1, size_hint_y=None)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.scroll.add_widget(self.chat_layout)

        self.input_box = TextInput(size_hint_y=None, height=50)
        send_btn = Button(text="Send", size_hint_y=None, height=50)
        logout_btn = Button(text="Logout", size_hint_y=None, height=50)

        send_btn.bind(on_press=self.reply)
        logout_btn.bind(on_press=self.logout)

        layout.add_widget(self.scroll)
        layout.add_widget(self.input_box)
        layout.add_widget(send_btn)
        layout.add_widget(logout_btn)

        self.add_widget(layout)

        self.selected_product = None
        self.add_message("Bot", "Welcome 🛍️ Ask product name")

    def add_message(self, sender, message):
        self.chat_layout.add_widget(Label(
            text=f"{sender}: {message}",
            size_hint_y=None,
            height=40
        ))

    def reply(self, instance):
        user_text = self.input_box.text.lower()
        self.add_message("You", user_text)

        products = load_json(PRODUCT_FILE)

        if user_text in products:
            self.selected_product = user_text
            self.add_message("Bot", f"Price: ₹{products[user_text]}")
            self.add_message("Bot", "Type 'buy' to confirm")

        elif user_text == "buy" and self.selected_product:
            orders = load_json(ORDER_FILE)
            order_id = str(len(orders) + 1)
            orders[order_id] = products[self.selected_product]
            save_json(ORDER_FILE, orders)

            self.add_message("Bot", "Order Confirmed ✅")
            self.selected_product = None

        else:
            self.add_message("Bot", "Product not found ❌")

        self.input_box.text = ""

    def logout(self, instance):
        self.manager.current = "login"

class SmartChatBot(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(AdminScreen(name="admin"))
        sm.add_widget(ChatScreen(name="chat"))
        return sm

if __name__ == "__main__":
    SmartChatBot().run()

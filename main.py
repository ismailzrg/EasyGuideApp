from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.uix.button import MDIconButton
from kivy.core.text import Label
from kivymd.uix.label import MDLabel
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDTextButton, MDFlatButton, MDRectangleFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivy.animation import Animation
from kivymd.uix.floatlayout import MDFloatLayout
from kivy_garden.mapview import MapView, MapMarker, MapMarkerPopup, MapSource, MapLayer
from kivymd.uix.backdrop import MDBackdrop
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.dropdown import DropDown
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.relativelayout import RelativeLayout
from plyer import gps
from kivy.graphics import Color, Line
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from kivymd.uix.pickers import MDTimePicker
from kivy.uix.modalview import ModalView
from googletrans import Translator
from deep_translator import GoogleTranslator
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import OneLineListItem
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse
from kivy.uix.label import Label
from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.progressbar import MDProgressBar

import webview
import os
import folium
import sqlite3
import re
import smtplib
import email.utils
import random
import requests
import json

# ////////////////////////////////////////////////////////////////
# ///////////////////// size window APP: /////////////////////////
Window.size = (350, 600)


# ////////////////////////////////////////////////////////////////
# ///////////////////// Data of Signup Form: /////////////////////
class SharedSignupData:
    name = None
    prename = None
    email = None
    password = None
    c_password = None
    code = None


# ////////////////////////////////////////////////////////////////
# ///////////////////// Data of Login Form: //////////////////////
class SharedLoginData:
    name = None
    prename = None
    email = None
    password = None


# ////////////////////////////////////////////////////////////////
# ///////////////////// Maps of Add Pharm/Doct: //////////////////
class MapDialog(ModalView):

    def __init__(self, main_screen, **kwargs):

        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False
        self.geolocator = Nominatim(user_agent="map_dialog")
        self.main_screen = main_screen  # Reference to the main screen

        layout = MDBoxLayout(orientation='vertical')
        self.map_view = MapView(
            lat=35.74537259990013, lon=0.5584349776587884, zoom=10,  # My Coordinates actuelle "relizane"
            map_source='osm'
        )
        self.map_view.bind(on_touch_down=self.on_map_touch_down1)
        Refrech_button = MDFlatButton(
            text="Actualisé",
            size_hint=(1, 0.1),
            md_bg_color=(1, 1, 1, 1)  # Set background color to white
        )
        Refrech_button.bind(on_release=self.update_location1)
        close_button = MDFlatButton(
            text="Close",
            size_hint=(1, 0.1),
            md_bg_color=(1, 1, 1, 1)  # Set background color to white
        )
        close_button.bind(on_release=self.dismiss)

        layout.add_widget(self.map_view)
        layout.add_widget(close_button)
        layout.add_widget(Refrech_button)
        self.add_widget(layout)

    def on_map_touch_down1(self, instance, touch):

        if touch.is_double_tap:
            if self.map_view.collide_point(*touch.pos):
                lat, lon = self.map_view.get_latlon_at(touch.x, touch.y)
                self.show_location_info1(lat, lon)
                self.dismiss()
                return True
        return False

    def show_location_info1(self, lat, lon):

        try:
            # Initialize the translator: translator = GoogleTranslator(source='auto', target='ar')
            location = self.geolocator.reverse((lat, lon), exactly_one=True)
            address = location.raw['address']
            name = (
                f"{address.get('road', "")} "
                f"{address.get('neighbourhood', "")} "
                f"{address.get('suburb', "")} "
                f"{address.get('city', "")}"
                f"{address.get('state', "")}"
            )
            city = address.get('city', address.get('town', address.get('village', 'N/A')))
            region = address.get('state', 'N/A')
            info = f"Latitude: {lat}\nLongitude: {lon}\nFull Address: {name}\nCity: {city}\nRegion: {region}"
            print(info)
            # Access to the elements of the main screen
            self.main_screen.ids.pm_address.text = name
            self.main_screen.ids.pm_lat.text = str(lat)
            self.main_screen.ids.pm_lon.text = str(lon)
        except Exception as e:
            info = f"Latitude: {lat}\nLongitude: {lon}\nUnable to fetch address"
            print(info)

    def update_location1(self, *args):

        try:
            # Use an IP-based geolocation service to get the user's location
            response = requests.get('http://ip-api.com/json/')
            data = response.json()
            if data['status'] == 'success':
                location_info = (f"IP: {data['query']}\n"
                                 f"City: {data['city']}\n"
                                 f"Region: {data['regionName']}\n"
                                 f"Country: {data['country']}\n"
                                 f"Latitude: {data['lat']}\n"
                                 f"Longitude: {data['lon']}")
                self.map_view.center_on(data['lat'], data['lon'])
                # Create the marker and add it
                marker = MapMarkerPopup(lat=data['lat'], lon=data['lon'])
                self.map_view.add_widget(marker)
            else:
                print("Could not fetch location")
        except requests.exceptions.RequestException:
            print("Error fetching location")

        # ////////////////////////////////////////////////////////////////


# ///////////////////// Market of Add Display_maps: //////////////////

class CustomMapMarker(MapMarkerPopup):
    def __init__(self, color=(1, 0, 0, 1), **kwargs):
        super().__init__(**kwargs)
        self.marker_label = None
        self.color = color
        self.size = (48, 48)  # Size of the marker
        self.bind(on_release=self.on_release_popup)

    def on_release_popup(self, instance):
        # Show or hide the label when the marker is clicked
        if self.marker_label is None:
            self.marker_label = MDCard(size_hint=(None, None), size=(180, 40), elevation=8)
            label = Label(text=self.popup_text, halign='center', color=(0, 0, 1, 1))
            self.marker_label.add_widget(label)
            self.add_widget(self.marker_label)
        else:
            self.remove_widget(self.marker_label)
            self.marker_label = None


class MapWithLines(MDFloatLayout):
    def __init__(self, display_screen, **kwargs):
        super().__init__(**kwargs)
        self.line_color = (0, 1, 0, 1)  # Green color for the lines
        self.screens = display_screen
        self.screens.ids.mapview.center_on(35.74537259990013, 0.5584349776587884)  # My Coordinates actuelle "relizane"
        self.screens.ids.mapview.zoom = 11
        self.line_routes = []
        self.routes_points = []

    def update_lines(self, marker_positions_):
        if len(marker_positions_) < 2:
            return
        with self.screens.ids.mapview.canvas:
            # Clear previous lines
            self.screens.ids.mapview.canvas.clear()
            Color(*self.line_color)
            points = []
            i = 1
            for lat, lon in marker_positions_:
                print(i, " | lat: ", lat, "lon: ", lon)
                i += 1
                x, y = self.screens.ids.mapview.get_window_xy_from(lat, lon, self.screens.ids.mapview.zoom)
                points.extend([x, y])
            Line(points=points, width=2)


class EasyGuide(MDApp):
    dialog = None

    def build(self):

        global ScreenManager
        ScreenManager = ScreenManager()
        ScreenManager.add_widget(Builder.load_file("pre_window.kv"))
        ScreenManager.add_widget(Builder.load_file("login.kv"))
        ScreenManager.add_widget(Builder.load_file("signup.kv"))
        ScreenManager.add_widget(Builder.load_file("valide_email.kv"))
        ScreenManager.add_widget(Builder.load_file("secc_valide.kv"))
        ScreenManager.add_widget(Builder.load_file("main.kv"))
        ScreenManager.add_widget(Builder.load_file("display_maps.kv"))

        # ------------------------------------
        # create table of users 'compte_user'
        conn = sqlite3.connect('easyguide.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE if not exists compte_user(
                  name text,
                  prename text,
                  email text PRIMARY KEY,
                  password text
                  )
        """)
        conn.commit()
        conn.close()

        # ------------------------------------
        # create table of points 'pharm_doct'
        conn = sqlite3.connect('easyguide.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE if not exists pharm_doct(
                  pd_name text PRIMARY KEY,
                  pd_desc text,
                  pd_address text,
                  pd_lat text,
                  pd_lon text,
                  pd_score integer,
                  pd_open text,
                  pd_close text
                  )
        """)
        conn.commit()
        conn.close()

        return ScreenManager

    # /////////////////////////////////////////////////////////////////////////////////////
    # /////////////////////////      Pre-window.kv part:     //////////////////////////////
    # /////////////////////////////////////////////////////////////////////////////////////

    def on_start(self):
        Clock.schedule_once(self.login, 3)

    def login(self, *args):
        ScreenManager.current = "login"

    # /////////////////////////////////////////////////////////////////////////////////////
    # /////////////////////////        Login.kv part:        //////////////////////////////
    # /////////////////////////////////////////////////////////////////////////////////////

    def check_email(self, u_email):
        try:
            parsed_email = email.utils.parseaddr(u_email.text.strip())
            if parsed_email[1] == '':
                return 0
            email_address = parsed_email[1]
            domain = email_address.split('@')[1]
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]+$", email_address):
                return 0
            return 1
        except Exception as e:
            return 0

    def connexion_access(self, username_input, password_input):

        if EasyGuide.check_email(self, username_input) == 0 or password_input.text.strip() == '':
            self.dialog = MDDialog(
                title="ERREURE ...",
                text="Verifie les donnees!...",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()
        else:
            conn = sqlite3.connect('easyguide.db')
            c = conn.cursor()
            c.execute("SELECT * from compte_user")
            email_list = []
            for i in c.fetchall():
                email_list.append(i[2])
            print(email_list)
            if username_input.text.strip() in email_list:
                conn1 = sqlite3.connect('easyguide.db')
                c1 = conn1.cursor()
                c1.execute(
                    f"SELECT name, prename, password from compte_user where email='{username_input.text.strip()}'")
                records = c1.fetchall()
                for record in records:
                    name, prename, password = record
                    if password_input.text.strip() == password:
                        SharedLoginData.name = name
                        SharedLoginData.prename = prename
                        username_input.text = ""
                        password_input.text = ""
                        ScreenManager.current = "main"

                        # Change the text of a label in main_screen
                        main_screen = self.root.get_screen('main')
                        main_screen.ids.data_profil.text = SharedLoginData.name + " " + SharedLoginData.prename
                        self.geolocator = Nominatim(user_agent="kivy_app")
                        # Fetch and display location after navigating to the special screen
                        Clock.schedule_once(self.update_location, 1)
                        self.full_pdlist()

                        conn1.commit()
                        conn1.close()
                    else:
                        self.dialog = MDDialog(
                            title="ERREURE ...",
                            text="incorrect password",
                            buttons=[
                                MDFlatButton(
                                    text="Fermer",
                                    text_color=self.theme_cls.primary_color,
                                    on_release=lambda x: self.dialog.dismiss()
                                ),
                            ],
                        )
                        self.dialog.open()
                conn.commit()
                conn.close
            else:
                self.dialog = MDDialog(
                    title="ERREURE ...",
                    text="incorrect email",
                    buttons=[
                        MDFlatButton(
                            text="Fermer",
                            text_color=self.theme_cls.primary_color,
                            on_release=lambda x: self.dialog.dismiss()
                        ),
                    ],
                )
                self.dialog.open()

    def reset_password(self, username_input):
        if EasyGuide.check_email(self, username_input) == 0 or username_input.text.strip() == '':
            self.dialog = MDDialog(
                title="ERREURE ...",
                text="Verifie Email!...",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()
        else:
            conn = sqlite3.connect('easyguide.db')
            c = conn.cursor()
            c.execute("SELECT * from compte_user")
            email_list = []
            for i in c.fetchall():
                email_list.append(i[2])
            print(email_list)
            conn.commit()
            conn.close()
            if username_input.text.strip() in email_list:
                conn1 = sqlite3.connect('easyguide.db')
                c1 = conn1.cursor()
                c1.execute(
                    f"SELECT name, prename, password from compte_user where email='{username_input.text.strip()}'")
                records = c1.fetchall()
                conn1.commit()
                conn1.close()
                for record in records:
                    name_, prename_, password_ = record

                sender_email = "zrgismail@gmail.com"
                password = "auzg cswm nutg vvrc"
                receiver_email = username_input.text.strip()
                print(receiver_email)
                smtp_server = "smtp.gmail.com"  # Replace with your email provider's SMTP server
                smtp_port = 587  # Replace with your email provider's SMTP port (might be different
                subject = "Reset Account's Password"
                message = f"Hello, {name_} {prename_} your password is:  {password_}."
                try:
                    # Create a secure connection with the server
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, password)

                    # Construct email message
                    email_content = f"From: {sender_email}\n"
                    email_content += f"To: {receiver_email}\n"
                    email_content += f"Subject: {subject}\n\n"
                    email_content += message

                    # Send the email
                    server.sendmail(sender_email, receiver_email, email_content)
                    server.quit()
                    print("Email sent successfully!")
                    self.dialog = MDDialog(
                        title="Le Mots de pass Renvoye vers ...",
                        text=receiver_email,
                        buttons=[
                            MDFlatButton(
                                text="Fermer",
                                text_color=self.theme_cls.primary_color,
                                on_release=lambda x: self.dialog.dismiss()
                            ),
                        ],
                    )
                    self.dialog.open()
                except Exception as e:
                    print(f"Error sending email: {e}")
                    self.dialog = MDDialog(
                        title="Failed Sending Email",
                        text="Error : {e}",
                        buttons=[
                            MDFlatButton(
                                text="Fermer",
                                text_color=self.theme_cls.primary_color,
                                on_release=lambda x: self.dialog.dismiss()
                            ),
                        ],
                    )
                    self.dialog.open()

            else:
                self.dialog = MDDialog(
                    title="ERREURE ...",
                    text="cette email ne trouve pas un compte!",
                    buttons=[
                        MDFlatButton(
                            text="Fermer",
                            text_color=self.theme_cls.primary_color,
                            on_release=lambda x: self.dialog.dismiss()
                        ),
                    ],
                )
                self.dialog.open()

    # /////////////////////////////////////////////////////////////////////////////////////
    # /////////////////////////        Signup.kv part:       //////////////////////////////
    # /////////////////////////////////////////////////////////////////////////////////////

    def CheckSignuoData(self, u_name, u_prename, u_email, u_password, u_cpassword):

        if u_name.text.strip() == '' or u_prename.text.strip() == '' or u_email.text.strip() == '' or u_password.text.strip() == '' or u_cpassword.text.strip() == '':
            return "missing information"
        elif EasyGuide.check_email(self, u_email) == 0:
            return "incorrect email format"
        elif u_password.text.strip() != u_cpassword.text.strip():
            return "password incorrect"
        else:
            return "data checked"

    def confirmation(self, u_name, u_prename, u_email, u_password, u_cpassword):

        SharedSignupData.name = u_name.text.strip()
        SharedSignupData.prename = u_prename.text.strip()
        SharedSignupData.email = u_email.text.strip()
        SharedSignupData.password = u_password.text.strip()
        SharedSignupData.c_password = u_cpassword.text.strip()
        SharedSignupData.code = random.randint(1000, 9999)
        if EasyGuide.CheckSignuoData(self, u_name, u_prename, u_email, u_password,
                                     u_cpassword) == "missing information":
            self.dialog = MDDialog(
                title="Erreur:",
                text="manque d'informations, complet le formulaire STP",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()
        elif EasyGuide.CheckSignuoData(self, u_name, u_prename, u_email, u_password,
                                       u_cpassword) == "incorrect email format":
            self.dialog = MDDialog(
                title="Erreur:",
                text="incorrect email format!!",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()
        elif EasyGuide.CheckSignuoData(self, u_name, u_prename, u_email, u_password,
                                       u_cpassword) == "password incorrect":
            self.dialog = MDDialog(
                title="Erreur:",
                text="les deux mots de pas ne sont pas compatible!!",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()
        else:
            sender_email = "zrgismail@gmail.com"
            password = "auzg cswm nutg vvrc"
            receiver_email = u_email.text.strip()
            print(receiver_email)
            smtp_server = "smtp.gmail.com"  # Replace with your email provider's SMTP server
            smtp_port = 587  # Replace with your email provider's SMTP port (might be different
            subject = "Confirmation code Account"
            message = f"Hello, {u_name.text.strip()} {u_prename.text.strip()} your confirmation code is:  {SharedSignupData.code}."
            try:
                # check  email if existed or no
                conn = sqlite3.connect('easyguide.db')
                c = conn.cursor()
                c.execute("SELECT * from compte_user")
                email_list = []
                for i in c.fetchall():
                    email_list.append(i[2])
                print(email_list)
                if receiver_email in email_list:
                    self.dialog = MDDialog(
                        title="Failed Sending Email",
                        text=" Email déja existe...",
                        buttons=[
                            MDFlatButton(
                                text="Fermer",
                                text_color=self.theme_cls.primary_color,
                                on_release=lambda x: self.dialog.dismiss()
                            ),
                        ],
                    )
                    self.dialog.open()
                else:
                    # Create a secure connection with the server
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, password)
                    # Construct email message
                    email_content = f"From: {sender_email}\n"
                    email_content += f"To: {receiver_email}\n"
                    email_content += f"Subject: {subject}\n\n"
                    email_content += message
                    # Send the email
                    server.sendmail(sender_email, receiver_email, email_content)
                    server.quit()
                    print("Email sent successfully!")
                    self.dialog = MDDialog(
                        title="Le Code de confermation envoye vers ...",
                        text=receiver_email,
                        buttons=[
                            MDFlatButton(
                                text="Fermer",
                                text_color=self.theme_cls.primary_color,
                                on_release=lambda x: self.dialog.dismiss()
                            ),
                        ],
                    )
                    self.dialog.open()
                    # presentation msg de confirmation
                    print(SharedSignupData.code, subject, message)
                    ScreenManager.current = "valide"
            except Exception as e:
                print(f"Error sending email: {e}")
                self.dialog = MDDialog(
                    title="Failed Sending Email",
                    text=" Email déja existe...",
                    buttons=[
                        MDFlatButton(
                            text="Fermer",
                            text_color=self.theme_cls.primary_color,
                            on_release=lambda x: self.dialog.dismiss()
                        ),
                    ],
                )
                self.dialog.open()

    # /////////////////////////////////////////////////////////////////////////////////////
    # /////////////////////////        Valide.kv part:       //////////////////////////////
    # /////////////////////////////////////////////////////////////////////////////////////

    def reconfirmation(self):

        sender_email = "zrgismail@gmail.com"
        password = "auzg cswm nutg vvrc"
        receiver_email = SharedSignupData.email
        print(receiver_email)
        smtp_server = "smtp.gmail.com"  # Replace with your email provider's SMTP server
        smtp_port = 587  # Replace with your email provider's SMTP port (might be different
        subject = "Confirmation code Account"
        message = f"Hello, {SharedSignupData.name} {SharedSignupData.prename} your confirmation code is:  {SharedSignupData.code}."
        print(SharedSignupData.code, subject, message)
        try:
            # Create a secure connection with the server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, password)

            # Construct email message
            email_content = f"From: {sender_email}\n"
            email_content += f"To: {receiver_email}\n"
            email_content += f"Subject: {subject}\n\n"
            email_content += message

            # Send the email
            server.sendmail(sender_email, receiver_email, email_content)
            server.quit()
            print("Email sent successfully!")
            self.dialog = MDDialog(
                title="Le Code Renvoye vers ...",
                text=receiver_email,
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()
        except Exception as e:
            print(f"Error sending email: {e}")
            self.dialog = MDDialog(
                title="Failed Sending Email",
                text="Error : {e}",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()

    def create_account(self, code_input):

        if code_input.text == str(SharedSignupData.code):
            conn = sqlite3.connect('easyguide.db')
            c = conn.cursor()
            insert = ("INSERT INTO compte_user VALUES(?,?,?,?)")
            mydata = (
            SharedSignupData.name, SharedSignupData.prename, SharedSignupData.email, SharedSignupData.password)
            c.execute(insert, mydata)
            conn.commit()
            conn.close()
            # --------------------------------------------------------------
            # clear the content of screens' widgets 'signup and valide_email
            screen_manager = self.root
            signup = screen_manager.get_screen('signup')
            signup.ids['u_name'].text = ''
            signup.ids['u_prename'].text = ''
            signup.ids['u_email'].text = ''
            signup.ids['u_password'].text = ''
            signup.ids['u_cpassword'].text = ''
            valide = screen_manager.get_screen('valide')
            valide.ids['code_input'].text = ''
            print("ur account created as seccessufly")
            ScreenManager.current = "secc_valide"
        else:
            self.dialog = MDDialog(
                title="Erreur",
                text="vérifiez votre code de confirmation ou appuyez sur le TextBUtton ci-dessous pour renvoyer le code à nouveau ...",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()

    # /////////////////////////////////////////////////////////////////////////////////////
    # /////////////////////////      Secc_valide.kv part:    //////////////////////////////
    # /////////////////////////////////////////////////////////////////////////////////////

    # /////////////////////////////////////////////////////////////////////////////////////
    # /////////////////////////         Main.kv part:        //////////////////////////////
    # /////////////////////////////////////////////////////////////////////////////////////

    # /////////////////////////////////////////////////////////
    #   Accueille     ////////////////////////////////////////

    def update_location(self, *args):

        main_screen = self.root.get_screen('main')
        try:
            # Use an IP-based geolocation service to get the user's location
            response = requests.get('http://ip-api.com/json/')
            data = response.json()
            if data['status'] == 'success':
                location_info = (f"{data['city']} "
                                 f"{data['regionName']} "
                                 f"{data['country']}: "
                                 f"{data['lat']} | "
                                 f"{data['lon']}"
                                 )
                main_screen.ids.u_location.text = location_info
            else:
                main_screen.ids.u_location.text = "Could not fetch location"
        except requests.exceptions.RequestException:
            main_screen.ids.u_location.text = "Error fetching location"

    def full_pdlist(self):

        accueille_screen = self.root.get_screen('main')
        conn = sqlite3.connect('easyguide.db')
        c = conn.cursor()
        c.execute(f"SELECT pd_name, pd_lat, pd_lon from pharm_doct")
        records = c.fetchall()
        for record in records:
            name, lat, lon = record
            accueille_screen.ids.container.add_widget(
                OneLineListItem(
                    text=f"{name} {lat} {lon}"
                )
            )

    # /////////////////////////////////////////////////////////
    #   Pharm/doct    ////////////////////////////////////////

    def show_map(self):

        screen_manager = self.root
        main_screen = screen_manager.get_screen('main')
        map_dialog = MapDialog(main_screen)
        map_dialog.open()

    def show_location_info(self, lat, lon):

        main_screen = self.root.get_screen('main')
        try:
            # Reverse geocode the coordinates
            location = self.geolocator.reverse((lat, lon), exactly_one=True)
            address = location.raw['address']
            name = address.get('name', 'N/A')
            city = address.get('city', address.get('town', address.get('village', 'N/A')))
            region = address.get('state', 'N/A')
            info = f"Latitude: {lat}\nLongitude: {lon}\nName: {name}\nCity: {city}\nRegion: {region}"
            print(info)
            main_screen.ids.pm_address.text = city
            main_screen.ids.pm_lat.text = str(lat)
            main_screen.ids.pm_lon.text = str(lon)
        except Exception as e:
            info = f"Latitude: {lat}\nLongitude: {lon}\nUnable to fetch address"
            print(info)

    def on_save(self, instance, time):

        main_screen = self.root.get_screen('main')
        main_screen.ids.pm_open.text = str(time)

    def show_time_picker(self):

        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_save)
        # Customize the size of the time picker
        time_dialog.size_hint = (1, .5)
        # Set the size in pixels            time_dialog.size = "350dp", "400dp"
        time_dialog.open()

    def on_save1(self, instance, time):

        main_screen = self.root.get_screen('main')
        main_screen.ids.pm_close.text = str(time)

    def show_time_picker1(self):

        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_save1)
        # Customize the size of the time picker
        time_dialog.size_hint = (1, .85)
        # Set the size in pixels            time_dialog.size = "350dp", "400dp"
        time_dialog.open()

    def add_pharmdoct(self, pm_name, pm_desc, pm_address, pm_lat, pm_lon, pm_score, pm_open, pm_close):

        if pm_name.text.strip() == '' or pm_desc.text.strip() == 'Pharm / Doct' or pm_address.text.strip() == '' or pm_lat.text.strip() == '' or pm_lon.text.strip() == '' or pm_score.text.strip() == '' or pm_open.text.strip() == '' or pm_close.text.strip() == '':
            self.dialog = MDDialog(
                title="Erreure: ",
                text="manque d'informations, complet le formulaire STP",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()
        else:
            try:
                # check  email if existed or no
                conn = sqlite3.connect('easyguide.db')
                c = conn.cursor()
                c.execute("SELECT * from pharm_doct")
                name_list = []
                for i in c.fetchall():
                    name_list.append(i[0])
                print(name_list)
                if pm_name.text.strip() in name_list:
                    self.dialog = MDDialog(
                        title="Erreur: ",
                        text=" Pharm / Doct déja existe ...",
                        buttons=[
                            MDFlatButton(
                                text="Fermer",
                                text_color=self.theme_cls.primary_color,
                                on_release=lambda x: self.dialog.dismiss()
                            ),
                        ],
                    )
                    self.dialog.open()
                else:
                    conn = sqlite3.connect('easyguide.db')
                    c = conn.cursor()
                    insert = ("INSERT INTO pharm_doct VALUES(?,?,?,?,?,?,?,?)")
                    mydata = (pm_name.text.strip(), pm_desc.text.strip(), pm_address.text.strip(), pm_lat.text.strip(),
                              pm_lon.text.strip(), int(pm_score.text), pm_open.text.strip(), pm_close.text.strip())
                    c.execute(insert, mydata)
                    conn.commit()
                    conn.close()
                    screen_manager = self.root
                    main_screen = screen_manager.get_screen('main')
                    main_screen.ids.container.add_widget(
                        OneLineListItem(
                            text=f"{main_screen.ids['pm_name'].text} {main_screen.ids['pm_lat'].text} {main_screen.ids['pm_lon'].text}"
                        )
                    )
                    main_screen.ids['pm_name'].text = ''
                    main_screen.ids['pm_address'].text = ''
                    main_screen.ids['pm_lat'].text = ''
                    main_screen.ids['pm_lon'].text = ''
                    main_screen.ids['pm_score'].text = ''
                    main_screen.ids['pm_open'].text = ''
                    main_screen.ids['pm_close'].text = ''
                    print("Pharm/Doct added as seccessufly")
                    self.dialog = MDDialog(
                        title="Valide",
                        text="Pharm / Doct \n ajoutez correctement...",
                        buttons=[
                            MDFlatButton(
                                text="Fermer",
                                text_color=self.theme_cls.primary_color,
                                on_release=lambda x: self.dialog.dismiss()
                            ),
                        ],
                    )
                    self.dialog.open()
            except Exception as e:
                self.dialog = MDDialog(
                    title="Erreur:",
                    text=str(e),
                    buttons=[
                        MDFlatButton(
                            text="Fermer",
                            text_color=self.theme_cls.primary_color,
                            on_release=lambda x: self.dialog.dismiss()
                        ),
                    ],
                )
                self.dialog.open()

    # /////////////////////////////////////////////////////////
    #   Chat          ////////////////////////////////////////

    def on_map_touch_down(self, instance, touch):

        main_screen = self.root.get_screen('main')
        # Check for double tap
        if touch.is_double_tap:
            mapview = main_screen.ids.id_mapview
            if mapview.collide_point(*touch.pos):
                lat, lon = mapview.get_latlon_at(*touch.pos)
                self.show_location_info(lat, lon)

    def duration_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.duration_on_save)
        # Customize the size of the time picker
        time_dialog.size_hint = (1, .5)
        # Set the size in pixels            time_dialog.size = "350dp", "400dp"
        time_dialog.open()

    def duration_on_save(self, instance, time):
        main_screen = self.root.get_screen('main')
        main_screen.ids.txt_duration.text = str(time)

    def generate_aco(self, txt_duration):
        from datetime import datetime, time, timedelta
        if txt_duration.text.strip() == '':
            self.dialog = MDDialog(
                title="Erreure: ",
                text="Remplis la durrée de travailleP",
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()
        else:
            duration_travail = datetime.strptime(txt_duration.text, "%H:%M:%S")
            hours = duration_travail.hour
            minutes = duration_travail.minute
            seconds = duration_travail.second
            duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

            # load data from pharm_doct table
            conn = sqlite3.connect('easyguide.db')
            c = conn.cursor()
            c.execute("select * from pharm_doct")
            markets = c.fetchall()
            conn.commit()
            conn.close()
            nodes_coor = []
            for market in markets:
                lat, lon = market[3], market[4]
                lat = float(lat)
                lon = float(lon)
                nodes_coor += [(lat, lon)]

            from aco_algorithme import EasyGuideACO
            my_instance = EasyGuideACO(colony_size=10, steps=50, nodes=nodes_coor, duration_trailer=duration)
            my_instance.run()
            best_tour = my_instance.global_best_tour
            best_time = my_instance.global_best_total_time
            runtime = my_instance.run_time
            labels = my_instance.labels
            print("************************/ -------- \************************")
            print("************************| Resultat |************************")
            print("duration de voyage de deligué est: ", duration)
            print("la durrée de best_time de tour est: ", best_time)
            print("la dure d'execution de algorithme est: ",runtime, " Sec")
            print("total nbr nodes de best_tour: ", len(best_tour))
            print("la listes de nodes: ", best_tour)
            for i in range(len(best_tour)):
                print(f"{i + 1} : {labels[int(best_tour[i])]}")
            # Generate the image Plot
            my_instance.plot(best_tour_=best_tour)
            # Generate the map
            my_map = my_instance.generate_map(nodes_coor, best_tour, labels)
            # Save the map to an HTML file
            my_map.save('aco_route_mapmaxmin.html')

            map_path = os.path.join(os.path.dirname(__file__), 'aco_route_mapmaxmin.html')
            file_url = f'file://{map_path}'

            # Create a web view window and load the HTML file
            # webview.create_window('HTML MapView Example', file_url)
            main_window_x = Window.left + (Window.width - 350) // 2
            main_window_y = Window.top - 20
            window = webview.create_window(
                title='ACO Route Map',  # Window title
                url=file_url,  # URL to the local HTML file
                width=350,  # Width of the window
                height=600,  # Height of the window
                # x=100,  # X position on the screen
                x=main_window_x,
                # y=100,  # Y position on the screen
                y=main_window_y,
                resizable=False,  # Allow the window to be resizable
                fullscreen=False,  # Do not start in fullscreen mode
                # min_size=(600, 350),  # Minimum size of the window
                easy_drag=True,  # Enable easy dragging of the window
                hidden=False,  # Show the window initially
                frameless=False,  # Include window frame
                background_color='#FFFFFF'  # Background color of the window
            )
            webview.start()


# /////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////          Run_app part:       //////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    EasyGuide().run()

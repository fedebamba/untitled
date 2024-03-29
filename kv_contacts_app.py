from kivy.app import App
from kivy.app import runTouchApp
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout

from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.properties import ListProperty, ObjectProperty, StringProperty

from kivy.clock import Clock
from functools import partial

import phonebook


class TrashBinPopup(Popup):
    def __init__(self):
        self.size_hint = (None, None)
        self.size = (Window.size[0] * .8, Window.size[1] * .8)
        self.title = "Trash Bin"

        super(TrashBinPopup, self).__init__()

        outerbox = BoxLayout(orientation="vertical")

        self.box = BoxLayout()
        self.box.add_widget(self.create_list())
        outerbox.add_widget(self.box)


        button1 = Button(text="Close trash Bin", size_hint=(.2, .2))
        button1.bind(on_press=self.dismiss)
        outerbox.add_widget(button1)
        self.add_widget(outerbox)

    def dismiss(self, *largs, **kwargs):
        ContactList.force_redrawing()
        super(TrashBinPopup, self).dismiss(*largs, **kwargs)

    def create_list(self):
        for x in [x for x in self.box.children]:
            self.box.remove_widget(x)
        box = BoxLayout(orientation="vertical")

        deleted_els = phonebook.contactManager.get_all_contacts_data(deleted=True)
        for x in deleted_els:
            el = BoxLayout(orientation="horizontal", size_hint=(.8, None), size=(300, 50))
            el.add_widget(Label(text=deleted_els[x]["Contact"], size_hint=(.8, None), size=(300, 50)))

            recovery_button = Button(text="Recover", size_hint=(.3, None), size=(300, 50), background_color=(.4, .8, .4, 1))
            recovery_button.bind(on_press=partial(self.recovery_el, x))
            el.add_widget(recovery_button)
            delete_button = Button(text="Delete", size_hint=(.3, None), size=(300, 50), background_color=(.8,.4,.4,1))
            delete_button.bind(on_press=partial(self.delete_el, x))
            el.add_widget(delete_button)
            box.add_widget(el)
        return box

    def recovery_el(self, name, x):
        phonebook.contactManager.recovery_contact(name)
        self.box.add_widget(self.create_list())

    def delete_el(self, name, x):
        phonebook.contactManager.hdelete_contact(name)
        self.box.add_widget(self.create_list())


class NewContactButton(Button):
    def __init__(self, parent):
        self._parent = parent
        super(NewContactButton, self).__init__()

    def on_press(self):
        print("ciao")
        ContactsScreen.contactDetailForm.draw_contact_details({}, username="", refresh=True)


class SortByDropDown(Button):
    def __init__(self, contact_list):
        self.contact_list = contact_list
        self.dropdown = DropDown()
        super(SortByDropDown, self).__init__()

        for field in [x[0] for x in phonebook.contactManager.retrieve_fields() if x[1]=='1']:
            btn = Button(text=field, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        self.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: self.sort_by(x))

    def sort_by(self, key):
        setattr(self, 'text', "Sort by {}".format(key))
        self.contact_list.draw_all_contacts(sortedby=key)


class SearchBox(BoxLayout):
    search_box = ObjectProperty(None)

    def __init__(self):
        super(SearchBox, self).__init__()
        self.search_box.bind(text = self.search)

    def search(self, instance, text):
        print(text)
        ContactList.search_tool(text)
        ContactList.force_redrawing(text)


class ContactList(BoxLayout):
    force_redrawing = None
    search_tool =None

    def __init__(self):
        self.sortedby = None
        self.search_string = None
        super(ContactList, self).__init__()

        self.draw_all_contacts()
        ContactList.force_redrawing = Clock.create_trigger(self.need_redraw)
        ContactList.search_tool = self.st

    def draw_all_contacts(self, sortedby="Name", searchby=None):
        self.sortedby = sortedby if sortedby is not None else self.sortedby
        for x in [x for x in self.children]:
            self.remove_widget(x)

        all_cd = phonebook.contactManager.get_all_contacts_data(require_in_fields=searchby)
        ls = list(all_cd.values())

        if len(ls) == 0:
            super(ContactList, self).add_widget(Label(text = "Seems like you don't have any contacts"))

        if sortedby is not None:
            ls = sorted(ls, key=lambda i: i[sortedby])

        for i in range(len(ls)):
            user_dict = ls[i]
            cb = ContactBox(user_dict["user"], user_dict)
            super(ContactList, self).add_widget(cb)

    def need_redraw(self, x):
        self.draw_all_contacts(searchby=self.search_string)

    def st(self, string=None):
        self.search_string = string


class ContactField(StackLayout):
    fieldname = StringProperty(None)
    value = StringProperty(None)

    def __init__(self, fieldname= "", value=""):
        self.fieldname = fieldname
        self.value = str(value)
        super(ContactField, self).__init__()


class ContactFieldEditable(StackLayout):
    fieldname = StringProperty(None)
    value = StringProperty(None)
    txt_inpt = ObjectProperty(None)

    def __init__(self, fieldname= "", value=""):
        self.fieldname = fieldname
        self.value = str(value)
        super(ContactFieldEditable, self).__init__()



class ContactBox(BoxLayout):
    pressed = ListProperty([0, 0])

    def __init__(self, username, user_info):
        self.username = username
        self.user_info = user_info
        super(ContactBox, self).__init__()
        for user_fieldname in user_info.keys():
            if user_fieldname in [x[0] for x in phonebook.contactManager.retrieve_fields() if x[1]=='1']:
                self.add_widget(ContactField(fieldname=user_fieldname, value=user_info[user_fieldname]))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            return True
        return super(ContactBox, self).on_touch_down(touch)

    def on_pressed(self, instance, pos):
        ContactsScreen.contactDetailForm.draw_contact_details(self.user_info, username=self.username)
        print(self.username)
        return True


class ContactDetails(StackLayout):
    def __init__(self):
        self.user_name = None
        self.user_data = {}
        self.orientation = "tb-lr"
        super(ContactDetails, self).__init__()

        self.form = StackLayout(size_hint=(1, .7), padding=[30,30,30,30], spacing=[5,5])
        for text in [x[0] for x in phonebook.contactManager.retrieve_fields()]:
            self.form.add_widget(ContactFieldEditable(fieldname=text, value=""))


        self.buttons = BoxLayout(size_hint=(1, None), size=(300, 30), orientation="horizontal")
        self.buttons.add_widget(Button(text="Update", size_hint=(.5,None), size=(300, 30), on_press=lambda x: self.update()))
        self.buttons.add_widget(Button(text="Delete", background_color=(.8,.4,.4,1), size_hint=(.5,None), size=(300, 30), on_press=lambda x: self.delete()))
        self.add_widget(self.buttons)
        self.add_widget(self.form)


        print([x for x in self.children])

        self.draw_contact_details()

    def update(self):
        dict={c.fieldname: c.txt_inpt.text for c in self.form.children}
        self.user_name = phonebook.contactManager.update_contact_data(self.user_name, dict)

        if dict["Contact"] == "":
            button = Button(text='Ok!', size_hint_y=.2)
            label = Label(text="Field contact can't be empty", size_hint_y=.8)
            box = BoxLayout(orientation="vertical")
            box.add_widget(label)
            box.add_widget(button)

            popup = Popup(title="", content=box, size_hint=(None, None), size=(400, 400))
            button.bind(on_press=popup.dismiss)
            popup.open()
            return

        ContactList.force_redrawing()
        self.draw_contact_details(self.user_data, self.user_name)
        print("update")


    def delete(self):
        print(self.user_name)
        phonebook.contactManager.delete_contact(self.user_name)
        ContactList.force_redrawing()
        self.draw_contact_details(None, None)
        print("delete")

    def draw_contact_details(self, user_data=None, username=None, refresh=False):
        self.user_name = username
        self.user_data = user_data

        if self.user_name is None:
            self.height, self.size_hint_y, self.opacity, self.disabled = 0, None, 0, True
        else:
            self.height, self.size_hint_y, self.opacity, self.disabled = 1000, 1, 1, False
            for c in self.form.children:
                if c.fieldname == "user":
                    c.value = self.user_name

            if self.user_data is not None:
                for c in self.form.children:
                    if c.fieldname != "user":
                        c.value = str(self.user_data[c.fieldname]) if c.fieldname in self.user_data.keys() else ""

            if refresh:
                for c in self.form.children:
                    c.value=""

class ContactsScreen(BoxLayout):
    header = ObjectProperty(None)
    right_col = ObjectProperty(None)
    left_col = ObjectProperty(None)
    contactDetailForm = None

    def __init__(self):
        super(ContactsScreen, self).__init__()


        #building the header
        self.header.add_widget(NewContactButton(self.right_col))

        trash = Button(text="trash", size_hint=(.15, None), size=(200, 50))
        trash.bind(on_press=lambda x: TrashBinPopup().open())
        self.header.add_widget(Label( size_hint=(.45, .6)))
        self.header.add_widget(trash)

        # building the left column


        contactlist_box = ContactList()
        contactlist_box.bind(minimum_height=contactlist_box.setter('height'))
        contactlist = ScrollView(size_hint=(1, 1), size=(Window.width, .7*Window.height))
        contactlist.add_widget(contactlist_box)

        self.left_col.add_widget(SortByDropDown(contactlist_box))
        self.left_col.add_widget(SearchBox())
        self.left_col.add_widget(contactlist)

        # building the right col
        ContactsScreen.contactDetailForm = ContactDetails()

        self.right_col.add_widget(self.contactDetailForm)


class ContactsApp(App):
    def build(self):
        return ContactsScreen()

# runTouchApp(ContactsApp().build())

ContactsApp().run()


"""
canvas.before:
    Color:
        rgba: 0,1,0,1
    Rectangle:
        size: self.size
        pos: self.pos

"""
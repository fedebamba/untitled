import json
import os
import csv

class ContactLoader:
    def __init__(self, file = "contact_data"):
        self.contact_data_file = file + ".json"
        self.fields = self.retrieve_fields("fields.csv")
        self.all_contacts = self.retrieve_all_contacts_data()

    def save_all_contacts_data(self):
        json_string = json.dumps(self.all_contacts)
        with open(self.contact_data_file, "w+") as json_file:
            json_file.write(json_string)

    def update_contact_data(self, user_id, user_dict):
        user_dict["deleted"] = False
        self.all_contacts[user_id] = user_dict

    def soft_delete_contact_data(self, user=None):
        if user is None:
            return
        self.all_contacts[user]["deleted"] = True

    def retrieve_fields(self, fieldfile):
        if not os.path.exists(fieldfile):
            with open(fieldfile, "w+", newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Contact", True])
                writer.writerow(["Name", True])
                writer.writerow(["Surname", True])
                writer.writerow(["Email", False])
                writer.writerow(["Phone", False])
                writer.writerow(["Notes", False])


        with open(fieldfile, "r+") as csv_file:
            reader = csv.reader(csv_file)
            return [row for row in reader]

    def hard_delete_contact_data(self, user=None):
        pass

    def retrieve_all_contacts_data(self):
        with open(self.contact_data_file, "r+") as json_file:
            f = json_file.read()
            if f == "":
                return {}

            return json.loads(f)


class ContactManager:
    def __init__(self):
        self.contact_loader = ContactLoader()

    def get_all_contacts_data(self, deleted=False):
        if len(self.contact_loader.all_contacts) == 0:
            return {}
        return { username: self.contact_loader.all_contacts[username] for username in self.contact_loader.all_contacts.keys() if self.condition(self.contact_loader.all_contacts[username], deleted=deleted) }

    def get_single_contact_data(self, username = None, force=False):
        if username is not None:
            if username in self.contact_loader.all_contacts.keys():
                if force or (self.condition(self.contact_loader.all_contacts[username]), False):
                    return self.contact_loader.all_contacts[username]
        return None

    def condition(self, user_data, deleted):
        if "deleted" in user_data.keys():
            return user_data["deleted"] == deleted
        return not deleted  # the assumption here is that if there's no "deleted" field, the element has not been deleted; the search should return true if deleted = false and vice versa

    def retrieve_fields(self):
        return self.contact_loader.fields

    def update_contact_data(self, username, user_data):
        if username is None or username == "":
            username = str(user_data["Name"]) + "-" + str(user_data["Surname"])

        user_data['user'] =username

        self.contact_loader.update_contact_data(username, user_data)
        self.contact_loader.save_all_contacts_data()
        return user_data['user']

    def delete_contact(self, username):
        self.contact_loader.soft_delete_contact_data(username)
        self.contact_loader.save_all_contacts_data()

contactManager = ContactManager()

import sys
from pathlib import Path
import pickle
from collections import UserDict
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value
        self.__value = None


class Name(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Phone(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value.isdigit() and len(value) == 12:
            self.__value = value
        else:
            raise Exception(
                f'Please enter phone number as 12 digits in format: "XXXXXXXXXXXX"')


class Birthday(Field):
    @ property
    def value(self):
        return self.__value

    @ value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, '%d-%m-%Y')
        except:
            Exception(f'Please enter birth date in format: DD-MM-YYYY')


class Record:

    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones.remove(phone)

    def edit_phone(self, phone, new_phone):
        self.remove_phone(phone)
        self.add_phone(new_phone)

    def __repr__(self):
        return f'{self.name.value}: {", ".join([phone.value for phone in self.phones])}'

    def days_to_birthday(self):
        today_day = datetime.now()
        today_year = datetime.now().year
        dif = today_day - self.birthday.value.replace(year=today_year)
        if dif >= 0:
            days_number = dif.days
        else:
            dif = self.birthday.value.replace(year=today_year+1) - today_day
            days_number = dif.days
        return days_number


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def iterator(self, number):
        i = 0
        n = number+1
        if i <= len(self.data):
            page_addrbook = {k: v for (k, v) in list(self.data.items())[i:n]}
            yield page_addrbook
            i = 1 + n
            n += 1
        raise StopIteration


# -------------------------------------------------------------------------

if Path('phonebook.bin').exists():  # <-- method was added: opening file with phonebook if so exist
    with open('phonebook.bin', 'rb') as file:
        CONTACTS = pickle.load(file)
else:
    CONTACTS = AddressBook()


def corrector(handler):
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except IndexError:
            print(
                'Erorr. \nYou should enter Name and/or Phone after command diveded by space!')
        except KeyError:
            print('There is no such Name in Phone Book')
        except Exception as error:
            print(f'Error {error}! \nEnter command once again, please.')
    return wrapper


def exit_func(_=None):
    # <-- method was added: saving phonebook in file on exits
    with open('phonebook.bin', 'wb') as file:
        pickle.dump(CONTACTS, file)
    sys.exit('Work done. Bye!')


@ corrector
def add_contact_handler(contact_info):
    name = contact_info[0]
    phone = contact_info[1]
    if CONTACTS.data.get(name):
        record = CONTACTS.data[name]
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        CONTACTS.add_record(record)
    print('New contact was added')


@ corrector
def find_contact_handler(contact_info):
    name = contact_info[0]
    record = CONTACTS.data[name]
    print(repr(record))


@ corrector
def delete_phone_handler(contact_info):
    name = contact_info[0]
    delete_phone = contact_info[1]
    record = CONTACTS.data[name]
    for phone in record.phones:
        if phone.value == delete_phone:
            record.remove_phone(phone)
            print(f'Phone number "{delete_phone}" for "{name}" was deleted')
            break
    else:
        print(f'No such number "{delete_phone} for name "{name}"')


@ corrector
def change_contact_handler(contact_info):
    name = contact_info[0]
    old_phone = contact_info[1]
    new_phone = contact_info[2]
    record = CONTACTS.data[name]
    for phone in record.phones:
        if phone.value == old_phone:
            record.edit_phone(phone, new_phone)
            print(
                f'Phone "{old_phone}" was changed on"{new_phone}" for "{name}"')
            break
    else:
        print(f'No such number "{old_phone} for name "{name}"')


@ corrector
def hello_handler(_=None):
    print('Hello! How can I help you?')


@ corrector
def all_contacts_show_handler(_=None):
    if len(CONTACTS.data) > 0:
        header = '| {:^15}| {:^15}|\n'.format('Name', 'Phone') + 35*'-'
        print(header)
        for name, record in CONTACTS.data.items():
            for phone in record.phones:
                line = ('| {:<15}| {:<15}|'.format(name, phone.value))
                print(line)
    else:
        print('There are no contacts in the phone book yet')


@ corrector  # <-- handler was added: find all contacts with simbols enterd by user
def contact_find_handler(contact_info):
    search_text = contact_info[0]
    found_contacts = []
    for name in CONTACTS.data:
        record = CONTACTS.data[name]
        if name.lower().find(search_text.lower()) >= 0:
            found_contacts.append(repr(record))
            continue
        for phone in record.phones:
            if str(phone.value).find(search_text) >= 0:
                found_contacts.append(f'{name}: {phone.value}')
    if not found_contacts:
        print("There is no contacts with such data")
    else:
        for contact in found_contacts:
            print(contact)


COMMANDS = {
    'exit': exit_func,
    'close': exit_func,
    'bye': exit_func,
    'add': add_contact_handler,
    'phone': find_contact_handler,
    'change': change_contact_handler,
    'delete': delete_phone_handler,
    'hello': hello_handler,
    'show all': all_contacts_show_handler,
    'find': contact_find_handler
}


def main():
    while True:
        user_input = input('Enter command and info: ')
        command_info = user_input.lower()
        for key in COMMANDS:
            if command_info.find(key) == 0 and command_info[len(key):len(key)+1].isalnum() == False:
                command = key
                contact_info = user_input[len(key):].split()
                COMMANDS[command](contact_info)
                break
        else:
            print("Command isn't correct!")


if __name__ == '__main__':
    main()

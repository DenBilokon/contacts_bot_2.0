import re

from collections import UserDict
from datetime import datetime, timedelta


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except IndexError:
            return "Give me name, old phone and new phone"
        except KeyError:
            return "Enter correct username"
        except ValueError:
            return "Enter username"
        except TypeError:
            return "Not enough params for command"
        except WrongLenPhone:
            return "Length of phone's number is wrong"
        except WrongTypePhone:
            return 'Incorrect phone number)))'

    return wrapper


HELP_TEXT = """This contact bot save your contacts 
    Global commands:
      'add' - add new contact. Input user name and phone
    Example: add User_name 095-xxx-xx-xx
      'change' - change users old phone to new phone. Input user name, old phone and new phone
    Example: change User_name 095-xxx-xx-xx 050-xxx-xx-xx
      'delete' - delete contact (name and phones). Input user name
    Example: delete User_name
      'phone' - show contacts of input user. Input user name
    Example: phone User_name
      'show all' - show all contacts
    Example: show all
      'exit/'.'/'bye'/'good bye'/'close' - exit bot
    Example: good bye"""


class WrongLenPhone(Exception):
    """ Exception for wrong length of the phone number """


class WrongTypePhone(Exception):
    """ Exception when a letter is in the phone number """


class AddressBook(UserDict):
    """ Dictionary class """

    def add_record(self, record):
        self.data[record.name.value] = record

    def remove_record(self, record):
        self.data.pop(record.name.value, None)

    def show_rec(self, name):
        return f'{name} (B-day: {rec.birthday}): {", ".join([str(phone.value) for phone in self.data[name].phones])}'

    def show_all_rec(self):
        return "\n".join(f'{rec.name} (B-day: {rec.birthday}): {", ".join([p.value for p in rec.phones])}' for rec in self.data.values())

    def change_record(self, name_user, old_record_num, new_record_num):
        record = self.data.get(name_user)
        if record:
            record.change(old_record_num, new_record_num)

    def iterator(self, n):
        records = list(self.data.keys())
        records_num = len(records)
        count = 0
        result = ''
        if n > records_num:
            n = records_num
        # for i in range(0, records_num, n):
        #     yield "\n".join(f'{rec.name} (B-day: {rec.birthday}): {", ".join([p.value for p in rec.phones])}' for rec in self.data.values())
        #     # yield [self.data[records[i + j]].show_contact() for j in range(n) if i + j < records_num]
        for rec in self.data.values():
            if count <= n:
                result += "\n".join(f'{rec.name} (B-day: {rec.birthday}): {", ".join([p.value for p in rec.phones])}')
                count += 1
        yield result

class Field:

    def __init__(self, value):
        self._value = value

    def __str__(self):
        return self._value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)

    @Field.value.setter
    def value(self, value):
        self._value = value


class Phone(Field):
    """Class for do phone number standard type"""

    @staticmethod
    def sanitize_phone_number(phone):
        new_phone = (
            str(phone).strip()
            .removeprefix("+")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        try:
            new_phone = [str(int(i)) for i in new_phone]
        except ValueError:
            raise WrongTypePhone('Input correct phone')

        else:
            new_phone = "".join(new_phone)
            if len(new_phone) == 12:
                return f"+{new_phone}"
            elif len(new_phone) == 10:
                return f"+38{new_phone}"
            else:
                raise WrongLenPhone("Length of phone's number is wrong")

    def __init__(self, value):
        super().__init__(value)
        self._value = Phone.sanitize_phone_number(value)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)

    @Field.value.setter
    def value(self, value):
        self._value = Phone.sanitize_phone_number(value)


class Birthday(datetime):
    """ Class for creating fields 'birthday' """

    @staticmethod
    def sanitize_date(year, month, day):
        try:
            birthday = datetime(year=year, month=month, day=day)
        except ValueError:
            print("Date is not correct. Please write date in format: yyyy-m-d")
        else:
            return str(birthday.date())

    def __init__(self, year, month, day):
        self.__birthday = self.sanitize_date(year, month, day)

    def __str__(self):
        return str(self.__birthday)

    def __repr__(self):
        return str(self.__birthday)

    @property
    def birthday(self):
        return self.__birthday

    @birthday.setter
    def birthday(self, year, month, day):
        self.__birthday = self.sanitize_date(year, month, day)


class Record:
    """ Class for record name or phones"""

    def __init__(self, name, phone=None, birthday=None):
        if birthday:
            self.birthday = Birthday(*birthday)
        else:
            self.birthday = None
        self.name = name
        self.phone = Phone(phone)
        self.phones = list()
        if isinstance(phone, Phone):
            self.phones.append(phone)

    def add_phone(self, phone):
        phone = Phone(phone)
        if phone.value:
            lst = [phone.value for phone in self.phones]
            if phone.value not in lst:
                self.phones.append(phone)
                return "Phone was added"
        else:
            raise ValueError("Phone number is not correct")

    def change(self, old_phone, new_phone):
        old_phone = Phone(old_phone)
        new_phone = Phone(new_phone)

        for phone in self.phones:
            if phone.value == old_phone.value:
                self.phones.remove(phone)
                self.phones.append(new_phone)
                return f'{old_phone} to {new_phone} changed'
            else:
                return print(f"Phone {old_phone} not found in the Record")

    def remove_phone(self, phone_num):
        phone = Phone(phone_num)

        for ph in self.phones:
            if ph.value == phone.value:
                self.phones.remove(ph)
                return f'Phone {phone_num} deleted'
            else:
                return f'Number {phone_num} not found'

    def add_user_birthday(self, year, month, day):
        self.birthday = Birthday.sanitize_date(int(year), int(month), int(day))

    def days_to_birthday(self):
        cur_date = datetime.now().date()
        cur_year = cur_date.year

        if self.birthday is not None:
            birthday = datetime.strptime(self.birthday, '%Y-%m-%d')
            this_year_birthday = datetime(cur_year, birthday.month, birthday.day).date()
            delta = this_year_birthday - cur_date
            if delta.days >= 0:
                return f"{self.name}'s birthday will be in {delta.days} days"
            else:
                next_year_birthday = datetime(cur_year + 1, birthday.month, birthday.day).date()
                delta = next_year_birthday - cur_date
                return f"{self.name}'s birthday will be in {delta.days} days"
        else:
            return f"{self.name}'s birthday is unknown"

    def get_contact(self):
        phones = ", ".join([str(p) for p in self.phones])
        return {
            "name": str(self.name.value),
            "phone": phones,
            "birthday": self.birthday
            }


ADDRESSBOOK = AddressBook()


def hello(*args):
    return "How can I help you?"


# Exit assistant
def bye(*args):
    return "Bye"


# README instructions
def help_user(*args):
    return HELP_TEXT


# Add user or user with phone to AddressBook
@input_error
def add_phone(*args):
    name = Name(str(args[0]).title())
    phone_num = (Phone(args[1]))
    rec = ADDRESSBOOK.get(name.value)
    if rec:
        rec.add_phone(phone_num)
    else:
        rec = Record(name, phone_num)
        ADDRESSBOOK.add_record(rec)
    return f'Contact {name} {phone_num} added'


# Change users contact to another contact
@input_error
def change(*args):
    name = Name(str(args[0]).title())
    old_phone = Phone(args[1])
    new_phone = Phone(args[2])
    ADDRESSBOOK.change_record(name.value, old_phone.value, new_phone.value)
    return f'User {name} changed {old_phone} to {new_phone}'


# Delete contact
@input_error
def delete_contact(*args):
    name = ADDRESSBOOK[args[0].title()]
    ADDRESSBOOK.remove_record(name)
    return f'Contact {args[0]} deleted'


# @input_error
def delete_phone(*args):
    name = Name(str(args[0]).title())
    phone = Phone(args[1])

    if name.value in ADDRESSBOOK:
        ADDRESSBOOK[name.value].remove_phone(phone.value)
        return f"Phone for {name.value} was delete"
    else:
        return f"Contact {name.value} does not exist"


# Show some contact
@input_error
def phone(*args):
    return ADDRESSBOOK.show_rec(str(args[0]).title())


# Show all contacts
def show_all(*args):
    if len(ADDRESSBOOK):
        return ADDRESSBOOK.show_all_rec()
    else:
        return 'AddressBook is empty'


@input_error
def show_list(*args):
    if len(ADDRESSBOOK):
        return ADDRESSBOOK.iterator(int(args[0]))
    else:
        return 'AddressBook is empty'


@input_error
def add_birthday(*args):
    name = Name(str(args[0]).title())
    birthday = tuple(re.split('\D', args[1]))

    if name.value in ADDRESSBOOK:
        ADDRESSBOOK[name.value].add_user_birthday(*birthday)
        return f"The Birthday for {name.value} was recorded"
    else:
        return f"Contact {name.value} does not exists"


@input_error
def days_to_bday(*args):
    name = Name(str(args[0]).title())
    if name.value in ADDRESSBOOK:
        if ADDRESSBOOK[name.value].birthday:
            days = ADDRESSBOOK[name.value].days_to_birthday()
            return days
        else:
            return f'{name.value} birthday is unknown'
    else:
        return f'Contact {name.value} does not exists'


COMMANDS = {
    hello: ["hello", "hi"],
    show_all: ["show all"],
    show_list: ["show list"],
    phone: ["phone"],
    add_phone: ["add contact"],
    change: ["change"],
    delete_contact: ["delete user"],
    delete_phone: ["delete phone"],
    add_birthday: ["add birthday"],
    days_to_bday: ['when celebrate'],
    help_user: ["help"],
    bye: [".", "bye", "good bye", "close", "exit"],
}


def parse_command(text: str):
    for comm, key_words in COMMANDS.items():
        for key_word in key_words:
            if text.startswith(key_word):
                return comm, text.replace(key_word, "").strip().split(" ")
    return None, None


# Функція спілкування з юзером і виконання функцій відповідно до команди
def run_bot(user_input):
    command, data = parse_command(user_input.lower())
    if not command:
        return "Incorrect input. Try again"
    return command(*data)


def main():
    while True:
        user_input = str(input(">>>> "))
        result = run_bot(user_input)
        if result == "Bye":
            print("Goodbye!")
            break
        print(result)


if __name__ == "__main__":
    main()

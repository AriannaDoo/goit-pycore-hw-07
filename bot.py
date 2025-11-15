from collections import UserDict
from datetime import datetime, timedelta

from storage import save_data, load_data


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону має містити рівно 10 цифр.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph
        return None

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError("Старий номер не знайдено.")
        self.phones[self.phones.index(phone_obj)] = Phone(new_phone)

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None

        today = datetime.today().date()
        bd = datetime.strptime(self.birthday.value, "%d.%m.%Y").date()
        next_bd = bd.replace(year=today.year)

        if next_bd < today:
            next_bd = next_bd.replace(year=today.year + 1)

        return (next_bd - today).days

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) if self.phones else "немає"
        birthday = self.birthday.value if self.birthday else "немає"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        result = []

        for record in self.data.values():
            if record.birthday:
                days = record.days_to_birthday()
                if days is not None and 0 <= days <= 7:
                    bd = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                    congrat_date = bd.replace(year=today.year)

                    if congrat_date < today:
                        congrat_date = congrat_date.replace(year=today.year + 1)

                    if congrat_date.weekday() >= 5:
                        congrat_date += timedelta(days=(7 - congrat_date.weekday()))

                    result.append(
                        {
                            "name": record.name.value,
                            "congratulation_date": congrat_date.strftime("%d.%m.%Y"),
                        }
                    )

        return result


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except (KeyError, ValueError, IndexError) as e:
            return f"Error: {e}"

    return inner


def parse_input(user_input):
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, *args


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    return "; ".join(p.value for p in record.phones)


@input_error
def add_birthday(args, book):
    name, date = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.add_birthday(date)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        return "Birthday not found."
    return record.birthday.value


def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."

    return "\n".join(f"{u['name']}: {u['congratulation_date']}" for u in upcoming)


def show_all(book):
    if not book.data:
        return "No contacts."
    return "\n".join(str(record) for record in book.values())


def main():
    book = load_data()
    if book is None:
        book = AddressBook()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ("close", "exit"):
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
            save_data(book)
        elif command == "change":
            print(change_contact(args, book))
            save_data(book)
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
            save_data(book)
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

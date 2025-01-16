import asyncio
import string
import platform
import subprocess
from secrets import choice
from typing import Union, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.create import create_credentials
from database.crud.get import get_credentials
from database.crud.update import update_password
from database.main import sessionmaker

DEFAULT_PASSWORD_LENGTH = 99
MSG_CLIPBOARD_COPIED = '[\u2713] Copied to clipboard: {text}'
MSG_CLIPBOARD_FAILED = '[!] Failed to copy to clipboard: {error}'
MSG_CLIPBOARD_UNSUPPORTED = '[!] Clipboard copy not supported on this OS.'
MSG_ENTER_PASSWORD_LENGTH = f'Enter password length (default is {DEFAULT_PASSWORD_LENGTH}): '
MSG_INVALID_LENGTH = '[!] Please enter a valid positive integer.'
MSG_EXISTING_CREDENTIALS = '\n[!] Credentials for \'{name}\' already exist.'
MSG_OPTIONS = '1. Add a new password manually\n2. Generate a new password\n3. Exit'
MSG_INVALID_OPTION = '[!] Invalid choice. Please select 1, 2, or 3.'
MSG_SUCCESS_EXIT = '[*] Successfully exited.'
MSG_GENERATE_PASSWORD = 'Do you want to generate a password? (y/n): '
MSG_INVALID_CHOICE = '[!] Invalid choice. Please enter y or n.'
MSG_ENTER_PASSWORD = 'Enter the password: '
MSG_SERVICE_NAME = 'Enter the service name: '
MSG_SERVICE_NAME_EMPTY = '[!] Service name cannot be empty.'
MSG_RESULT = '\n[***] Result:'
MSG_SERVICE_NAME_OUTPUT = 'Service Name: {name}'
MSG_PASSWORD_OUTPUT = 'Password: {password}'
MSG_ERROR_OCCURRED = '[!] An error occurred: {error}'
MSG_GET_PASSWORD = 'Do you want to get password? (y/n): '
MSG_CHOSE_123 = 'Choose an option (1/2/3): '
MSG_MUST_BE_POSITIVE = '[!] Password length must be positive.'


def copy_to_clipboard(
        text: str
) -> None:
    """
    Copies the given text to the clipboard, depending on the operating system.

    Args:
        text (str): The text to copy to the clipboard.
    """
    system = platform.system()
    try:
        if system == 'Linux':
            try:
                subprocess.run(['wl-copy'], input=text.encode(), check=True)
            except FileNotFoundError:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode(), check=True)
        elif system == 'Darwin':
            subprocess.run(['pbcopy'], input=text.encode(), check=True)
        elif system == 'Windows':
            import pyperclip
            pyperclip.copy(text)
        else:
            print(MSG_CLIPBOARD_UNSUPPORTED)
            return

        print(MSG_CLIPBOARD_COPIED.format(text=text))
    except Exception as e:
        print(MSG_CLIPBOARD_FAILED.format(error=e))


async def generate_password(
        default_length: int = DEFAULT_PASSWORD_LENGTH
) -> str:
    """
    Generates a secure password using a cryptographically strong random number generator.

    Args:
        default_length (int): The default length of the password if the user doesn't specify one.

    Returns:
        str: A randomly generated secure password.
    """
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    punctuation = string.punctuation
    split_chars = list(lowercase + uppercase + digits + punctuation)

    while True:
        length = input(MSG_ENTER_PASSWORD_LENGTH)
        if not length:
            length = default_length
        try:
            length = int(length)
            if length <= 0:
                raise ValueError(MSG_MUST_BE_POSITIVE)
            break
        except ValueError:
            print(MSG_INVALID_LENGTH)

    return ''.join(choice(split_chars) for _ in range(length))


async def handle_existing_credentials(
        session: AsyncSession, 
        name: str
) -> Union[Tuple[str, str], str]:
    """
    Handles the case where credentials already exist.

    Returns:
        Union[Tuple[str, str], str]: Updated credentials or an exit message.
    """
    while True:
        print(MSG_EXISTING_CREDENTIALS.format(name=name))
        print(MSG_OPTIONS)
        user_choice = input(MSG_CHOSE_123).strip()

        if user_choice == '1':
            password = input(MSG_ENTER_PASSWORD)
        elif user_choice == '2':
            password = await generate_password()
        elif user_choice == '3':
            return MSG_SUCCESS_EXIT
        else:
            print(MSG_INVALID_OPTION)
            continue

        await update_password(
            session=session,
            credentials_name=name,
            new_password=password,
        )
        copy_to_clipboard(password)
        return name, password


async def handle_new_credentials(
        session: AsyncSession, 
        name: str
) -> Union[Tuple[str, str], str]:
    """
    Handles the creation of new credentials.

    Returns:
        Union[Tuple[str, str], str]: New credentials or an exit message.
    """
    while True:
        action = input(MSG_GENERATE_PASSWORD).strip().lower()
        if action == 'y':
            password = await generate_password()
            break
        elif action == 'n':
            password = input(MSG_ENTER_PASSWORD)
            break
        else:
            print(MSG_INVALID_CHOICE)

    await create_credentials(
        session=session,
        credentials_name=name,
        credentials_password=password
    )
    copy_to_clipboard(password)
    return name, password


async def main(
        session: AsyncSession
) -> Union[Tuple[str, str], str]:
    """
    Main logic for handling credentials.

    Returns:
        Union[Tuple[str, str], str]: Credentials or an exit message.
    """
    name = input(MSG_SERVICE_NAME).strip()

    if not name:
        return MSG_SERVICE_NAME_EMPTY

    credentials = await get_credentials(
        session=session,
        credentials_name=name
    )
    while True:
        if credentials:
            action = input(MSG_GET_PASSWORD).strip().lower()
            if action == 'y':
                password = credentials.password
                copy_to_clipboard(password)
                return credentials.name, password
            elif action == 'n':
                handler = handle_existing_credentials if credentials.name == name else handle_new_credentials
                return await handler(session, name)
            else:
                print(MSG_INVALID_CHOICE)
        else:
            handler = handle_existing_credentials if credentials and credentials.name == name else handle_new_credentials
            return await handler(session, name)



async def run():
    """
    Entry point of the application. Manages the database session.
    """
    async with sessionmaker() as session:
        try:
            credentials = await main(session)
            print(MSG_RESULT)
            if isinstance(credentials, tuple):
                print(MSG_SERVICE_NAME_OUTPUT.format(name=credentials[0]))
                print(MSG_PASSWORD_OUTPUT.format(password=credentials[1]))
            else:
                print(credentials)
        except Exception as e:
            print(MSG_ERROR_OCCURRED.format(error=e))


if __name__ == '__main__':
    asyncio.run(run())

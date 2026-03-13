from __future__ import annotations

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings
from colorama import Fore, Style
from rich.table import Table
from rich.style import Style as RichStyle
from rich.text import Text
from rich import box
from tabulate import tabulate
from prompt_toolkit.formatted_text import FormattedText
import random
import inquirer
import urwid

import typing

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, Iterable

# Create Pseudo-Terminal tricking utilities in thinking they are executed in a real terminal, not a subprocess
import pty
import select
import os
import subprocess

# For utilties like less, with pagination
# ANSI escape sequence to clear the current line
CLEAR_LINE = "\033[2K\r"


def execute(args=["ls"], data=None):
    try:
        # Create a pseudo-terminal
        master_fd, slave_fd = pty.openpty()

        # Run the command in a subprocess connected to the pseudo-terminal
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE if data else slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            text=True,
        )

        if data:
            process.communicate(input=data)
        else:
            # Listen for both user input and subprocess output
            while True:
                # Use select to monitor both the terminal and the subprocess
                rlist, _, _ = select.select([master_fd, sys.stdin], [], [])

                if master_fd in rlist:
                    try:
                        output = os.read(master_fd, 1024).decode()
                        if output:
                            print(output, end="")
                            process.stdin.write("q")
                        else:
                            break  # Process finished
                    except OSError:
                        break  # Error or process terminated

                if sys.stdin in rlist:
                    user_input = os.read(sys.stdin.fileno(), 1024)
                    os.write(master_fd, user_input)  # Send user input to the process

        os.close(master_fd)
        os.close(slave_fd)

    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("stderr:", e.stderr.decode("utf-8"))


def less(file_path):
    p = os.pipe()
    less = subprocess.Popen("less", stdin=p[0])
    cmd = subprocess.Popen("whatever", stdout=p[1])
    os.close(p[0])
    os.close(p[1])
    less.wait()


def bat(file_path, paging=False):
    if not paging:
        process = execute(["bat", "--no-pager", "--color=always", file_path])
        process.stdin.write("q")  # q should quit most pagers
        return process
    return execute(["bat", "--paging=always", "--color=always", file_path])


def cat(file_path):
    return execute(["cat", file_path])


def horizontal_menu():
    global final_choice
    final_choice = None

    def exit_program(key):
        raise urwid.ExitMainLoop()

    class MenuButton(urwid.Button):
        def __init__(
            self,
            caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
            callback: Callable[[MenuButton], typing.Any],
        ) -> None:
            super().__init__("", on_press=callback)
            self._w = urwid.AttrMap(
                urwid.SelectableIcon(["  \N{BULLET} ", caption], 2),
                None,
                "selected",
            )

    class SubMenu(urwid.WidgetWrap[MenuButton]):
        def __init__(
            self,
            caption: str | tuple[Hashable, str],
            choices: Iterable[urwid.Widget],
        ) -> None:
            super().__init__(
                MenuButton([caption, "\N{HORIZONTAL ELLIPSIS}"], self.open_menu)
            )
            line = urwid.Divider("\N{LOWER ONE QUARTER BLOCK}")
            listbox = urwid.ListBox(
                urwid.SimpleFocusListWalker(
                    [
                        urwid.AttrMap(urwid.Text(["\n  ", caption]), "heading"),
                        urwid.AttrMap(line, "line"),
                        urwid.Divider(),
                        *choices,
                        urwid.Divider(),
                    ]
                )
            )
            self.menu = urwid.AttrMap(listbox, "options")

        def open_menu(self, button: MenuButton) -> None:
            top.open_box(self.menu)

    class Choice(urwid.WidgetWrap[MenuButton]):
        def __init__(
            self,
            caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        ) -> None:
            super().__init__(MenuButton(caption, self.item_chosen))
            self.caption = caption

        def item_chosen(self, button: MenuButton) -> None:
            response = urwid.Text(["  You chose ", self.caption, "\n"])
            global final_choice
            final_choice = self.caption
            done = MenuButton("Ok", exit_program)
            response_box = urwid.Filler(urwid.Pile([response, done]))
            top.open_box(urwid.AttrMap(response_box, "options"))

    menu_top = SubMenu(
        "Main Menu",
        [
            SubMenu(
                "Applications",
                [
                    SubMenu(
                        "Accessories",
                        [
                            Choice("Text Editor"),
                            Choice("Terminal"),
                        ],
                    )
                ],
            ),
            SubMenu(
                "System",
                [
                    SubMenu("Preferences", [Choice("Appearance")]),
                    Choice("Lock Screen"),
                ],
            ),
        ],
    )
    palette = [
        (None, "light gray", "black"),
        ("heading", "black", "light gray"),
        ("line", "black", "light gray"),
        ("options", "dark gray", "black"),
        ("focus heading", "white", "dark red"),
        ("focus line", "black", "dark red"),
        ("focus options", "black", "light gray"),
        ("selected", "white", "dark blue"),
    ]
    focus_map = {
        "heading": "focus heading",
        "options": "focus options",
        "line": "focus line",
    }

    class HorizontalBoxes(urwid.Columns):
        def __init__(self) -> None:
            super().__init__([], dividechars=1)

        def open_box(self, box: urwid.Widget) -> None:
            if self.contents:
                del self.contents[self.focus_position + 1 :]
            self.contents.append(
                (
                    urwid.AttrMap(box, "options", focus_map),
                    self.options(urwid.GIVEN, 24),
                )
            )
            self.focus_position = len(self.contents) - 1

    top = HorizontalBoxes()
    top.open_box(menu_top.menu)
    urwid.MainLoop(urwid.Filler(top, "middle", 10), palette).run()
    return final_choice


def cascading_menu():
    # default
    global final_choice
    final_choice = None

    class CascadingBoxes(urwid.WidgetPlaceholder):
        max_box_levels = 4

        def __init__(self, box: urwid.Widget) -> None:
            super().__init__(urwid.SolidFill("/"))
            self.box_level = 0
            self.open_box(box)

        def open_box(self, box: urwid.Widget) -> None:
            self.original_widget = urwid.Overlay(
                urwid.LineBox(box),
                self.original_widget,
                align=urwid.CENTER,
                width=(urwid.RELATIVE, 80),
                valign=urwid.MIDDLE,
                height=(urwid.RELATIVE, 80),
                min_width=24,
                min_height=8,
                left=self.box_level * 3,
                right=(self.max_box_levels - self.box_level - 1) * 3,
                top=self.box_level * 2,
                bottom=(self.max_box_levels - self.box_level - 1) * 2,
            )
            self.box_level += 1

        def keypress(self, size, key: str) -> str | None:
            if key == "esc" and self.box_level > 1:
                self.original_widget = self.original_widget[0]
                self.box_level -= 1
                return None
            return super().keypress(size, key)

    def menu_button(caption, callback):
        button = urwid.Button(caption, on_press=callback)
        # urwid.connect_signal(button, 'click', callback)
        return urwid.AttrMap(button, None, focus_map="reversed")

    def sub_menu(caption, choices):
        contents = menu_callback(caption, choices)

        def open_menu(button):
            return top.open_box(contents)

        return menu_button([caption, "..."], open_menu)

    def menu_callback(title, choices):
        body = [urwid.Text(title), urwid.Divider(), *choices]
        # body.extend(choices)
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def item_chosen(button):
        response = urwid.Text(["You chose", button.label, "\n"])
        global final_choice
        final_choice = button.label
        done = menu_button("Ok", exit_program)
        top.open_box(urwid.Filler(urwid.Pile([response, done])))

    def exit_program(button):
        raise urwid.ExitMainLoop()

    menu_top = menu_callback(
        "Main Menu",
        [
            sub_menu(
                "Applications",
                [
                    sub_menu(
                        "Accessories",
                        [
                            menu_button("Text Editor", item_chosen),
                            menu_button("Terminal", item_chosen),
                        ],
                    ),
                ],
            ),
            sub_menu(
                "System",
                [
                    sub_menu(
                        "Preferences",
                        [menu_button("Appearance", item_chosen)],
                    ),
                    menu_button("Lock Screen", item_chosen),
                ],
            ),
        ],
    )
    top = CascadingBoxes(menu_top)
    urwid.MainLoop(top, palette=[("reversed", "standout", "")]).run()
    return final_choice


def menu(title="Pythons", choices="Chapman Cleese Gilliam Idle Jones Palin".split()):
    # default
    global final_choice
    final_choice = None

    def exit_program(button):
        raise urwid.ExitMainLoop()

    # default menu callback
    def item_chosen(button, choice):
        response = urwid.Text(["You chose ", choice, "\n"])
        global final_choice
        final_choice = choice
        done = urwid.Button("Ok")
        urwid.connect_signal(done, "click", exit_program)
        main.original_widget = urwid.Filler(
            urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")])
        )

    def menu_callback(
        title="Pythons", choices="Chapman Cleese Gilliam Idle Jones Palin".split()
    ):
        body = [urwid.Text(title), urwid.Divider()]
        for c in choices:
            button = urwid.Button(c)
            urwid.connect_signal(button, "click", item_chosen, c)
            body.append(urwid.AttrMap(button, None, focus_map="reversed"))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    main = urwid.Padding(menu_callback(title, choices), left=2, right=2)
    top = urwid.Overlay(
        main,
        urwid.SolidFill("\N{MEDIUM SHADE}"),
        align="center",
        width=("relative", 60),
        valign="middle",
        height=("relative", 60),
        min_width=20,
        min_height=9,
    )
    urwid.MainLoop(top, palette=[("reversed", "standout", "")]).run()
    return final_choice


# checkbox
import os
import subprocess
import sys

import types

import subprocess
import json


"""
from base64 import standard_b64encode

# Basic icat (without subprocess)
def serialize_gr_command(**cmd):
    payload = cmd.pop("payload", None)
    cmd = ",".join(f"{k}={v}" for k, v in cmd.items())
    ans = []
    w = ans.append
    w(b"\033_G"), w(cmd.encode("ascii"))
    if payload:
        w(b";")
        w(payload)
    w(b"\033\\")
    return b"".join(ans)


def write_chunked(**cmd):
    data = standard_b64encode(cmd.pop("data"))
    while data:
        chunk, data = data[:4096], data[4096:]
        m = 1 if data else 0
        sys.stdout.buffer.write(serialize_gr_command(payload=chunk, m=m, **cmd))
        sys.stdout.flush()
        cmd.clear()


def delete_image(delete_type, **kwargs):
    delete_command = {"a": "d", "d": delete_type}
    delete_command.update(kwargs)
    delete_sequence = serialize_gr_command(**delete_command)
    sys.stdout.buffer.write(delete_sequence)
    sys.stdout.flush()


def icat(path):
    with open(path, "rb") as f:
        write_chunked(a="T", f=100, data=f.read())


"""


def icat(img_path):
    if not img_path:
        raise Exception("No image path provided")
    # Automatically expand ~ to the full home directory path
    img_path = os.path.expanduser(img_path)

    args = ["kitten", "icat", img_path]
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        print(result.stdout.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("icat stderr:", e.stderr.decode("utf-8"))


def print_jq(data, jq_filter="."):
    # Convert the Python data to JSON string
    json_str = json.dumps(data)

    # Run jq as a subprocess to pretty-print the JSON
    try:
        result = subprocess.run(
            ["jq", jq_filter, "-C"],
            input=json_str.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        print(result.stdout.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("jq stderr:", e.stderr.decode("utf-8"))


def install_rich(show_locals=True):
    from rich.console import Console
    from rich.traceback import install, Traceback

    install(show_locals=show_locals)
    return Console()
    # print = console.print


def exception_with_traceback(message):
    tb = None
    depth = 0
    while True:
        try:
            frame = sys._getframe(depth)
            depth += 1
        except ValueError as exc:
            break

        tb = types.TracebackType(tb, frame, frame.f_lasti, frame.f_lineno)

    return Exception(message).with_traceback(tb)


def prettifyTable(table):
    bg_col = "#000000"

    # Set the background color to purple
    table.style = RichStyle(bgcolor=bg_col)
    table.background_color = "green"

    # Set font color for the table
    table.color = "white"

    # Set background color for each row
    row_colors = [bg_col]
    for i, row in enumerate(table.rows):

        row.style = RichStyle(bgcolor=row_colors[i % len(row_colors)])

        return table


def extendTableDF(table, df, caption=None):
    # Add columns to the table
    for column in df.columns:
        table.add_column(str(column), style="cyan", no_wrap=True)

    # Add rows to the table
    for _, row in df.iterrows():
        row_data = [str(cell) for cell in row]
        table.add_row(*row_data)

    # Set other formatting options
    table.title = "Details"
    if caption != None:
        table.caption = caption
        table.caption_style = "bold yellow"

    table.border_style = "blue"

    return table


def getPrettyTable(dictionary, caption=""):
    import pandas as pd

    return prettifyTable(
        extendTableDF(
            Table(show_header=True, header_style="bold magenta"),
            pd.DataFrame(dictionary),
            caption=caption,
        )
    )


def printDF(DF, full=False, useTabulate=False, caption="Retrieved by Sql-Connection"):
    import pandas as pd

    try:

        if isinstance(DF, list):
            DF = pd.DataFrame(DF)  # Convert list to DataFrame
        if DF is not None and not DF.empty:
            if full:
                pd.set_option("display.max_columns", None)  # Show all columns
                # None means no truncation
                pd.set_option("display.max_colwidth", None)
                # pd.set_option('display.max_colwidth', None)
                pd.set_option("display.max_rows", None)  # Show all rows

            if useTabulate:
                table = tabulate(DF, headers="keys", tablefmt="psql", showindex=False)
            else:
                table = getPrettyTable(DF, caption=caption)
                # prettifyTable(extendTableDF(
                #    Table(show_header=True, header_style="bold #456000"), DF))
                # Update the style of the table
                table.row_styles = ["none", "dim"]
                table.box = box.SQUARE_DOUBLE_HEAD

            # print(DF)
            console.print(table)
            if full:
                pd.reset_option("display.max_columns")
                # pd.reset_option('display.max_colwidth')
                pd.reset_option("display.max_colwidth")
                pd.reset_option("display.max_rows")
        else:
            print("DataFrame is not set, can't print!")
    except Exception as e:
        print(e)


def table_to_df(table: Table):
    """Convert a rich.Table obj into a pandas.DataFrame obj with any rich formatting removed from the values.
    Args:
        rich_table (Table): A rich Table that should be populated by the DataFrame values.
    Returns:
        DataFrame: A pandas DataFrame with the Table data as its values."""
    import pandas as pd

    table_data = {
        x.header: [Text.from_markup(y).plain for y in x.cells] for x in table.columns
    }
    return pd.DataFrame(table_data)


class ANSIConsoleNavigation:
    """
    VERY SLOW
    - Position the Cursor:
     \033[<L>;<C>H
        Or
     \033[<L>;<C>f
     puts the cursor at line L and column C.
    - Move the cursor up N lines:
     \033[<N>A
    - Move the cursor down N lines:
     \033[<N>B
    - Move the cursor forward N columns:
     \033[<N>C
    - Move the cursor backward N columns:
     \033[<N>D

    - Clear the screen, move to (0,0):
     \033[2J
    - Erase to end of line:
     \033[K

    - Save cursor position:
     \033[s
    - Restore cursor position:
     \033[u
    """

    LINE_UP = "\033[1A"
    LINE_CLEAR = "\x1b[2K"

    CURSOR_SAVE = "\033[s"
    CURSOR_RESTORE = "\033[u"

    @staticmethod
    def save():
        sys.stdout.write(ANSIConsoleNavigation.CURSOR_SAVE)  # save pos

    @staticmethod
    def restore():
        sys.stdout.write(ANSIConsoleNavigation.CURSOR_RESTORE)  # restpre pos

    @staticmethod
    def move_up(N):
        # sys.stdout.write(f"\033[<{N}>A")  # Cursor up one line
        for _ in range(N):
            sys.stdout.write(ANSIConsoleNavigation.LINE_UP)  # "\033[F")


def clear_screen():
    console.clear()
    os.system("cls" if os.name == "nt" else "clear")


def find_option_line(option):
    try:
        # Execute findstr command and capture its output
        output = subprocess.check_output(
            f'findstr /N /C:"{option}" *', shell=True, text=True
        )

        # Parse the line number from the output
        line_number = int(output.split(":")[0])
        return line_number - 1  # Adjust for 0-based indexing
    except (subprocess.CalledProcessError, ValueError, IndexError):
        return -1  # Option not found


def move_cursor(x, y):
    # ANSI escape code to move cursor to (x, y)
    print(f"\033[{y};{x}H", end="")


def replace_line(line, new_text):
    move_cursor(0, line + 1)  # Adjust line number by 1 (1-based index)
    # ANSI escape code to clear the line and print new text
    print("\033[K" + new_text, end="")


def checkbox_input(title, options, multiselect=True, min_selection_count=0):
    from pick import pick

    return pick(
        options, title, multiselect=multiselect, min_selection_count=min_selection_count
    )


def print_large_text(text):
    with console.pager():
        # console.print(make_test_card())
        console.print(text)


def remove_umlauts(input_string):
    umlaut_map = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ß": "ss",
    }

    for umlaut, replacement in umlaut_map.items():
        input_string = input_string.replace(umlaut, replacement)

    return input_string


def exitPrompt(text):
    """Returns False if input was x or q. Else returns data"""
    text = " ".join(decorate_array_with_colorama(text.split(" ")))
    data = autocompleteprompt(
        prompt_message=text, lookupTable=[], bottom_toolbar=f"q'/'x to exit"
    )

    if data == "x" or data == "q":
        return False
    return data
    """
def exitInputPrompt(text):
    data = input(
        f"{text} ('{Fore.RED}q{Style.RESET_ALL}'/'{Fore.RED}x{Style.RESET_ALL}' to exit):")
    if data == 'x' or data == 'q':
        return False
    return data    
    """


def get_boolean_input(prompt):
    Y_N_Default = f"({Fore.GREEN}Y{Style.RESET_ALL}/{Fore.RED}N{Style.RESET_ALL})"
    while True:
        user_input = input(" ".join([prompt, Y_N_Default]))
        user_input = user_input.lower().strip()

        if user_input == "yes" or user_input == "y" or user_input == "true":
            return True
        elif (
            user_input == ""
            or user_input == "no"
            or user_input == "n"
            or user_input == "false"
        ):
            return False
        else:
            return False


# adjust this method to work like a cd command, in that you can navigate into objects like they are directories, and therefore change the context everytime to their
# current object. In a similar fashion there will be a chain "tree-like" structure build which helps pointing the inside of an object pack to its parent
# Node Current = {"previous" : parent, "next": List[Nodes], val: 0} ...


def get_contextual_input(local_variables):
    # Get array of variable values
    variables_array = list(local_variables.keys())
    selected_variable = autocompleteprompt(
        "Choose a variable to obtain its value: ",
        lookupTable=variables_array,
        bottom_toolbar=str(variables_array),
    )

    if selected_variable not in variables_array:
        return

    # Get the value of the selected variable
    if selected_variable in local_variables:
        value = local_variables[selected_variable]
        if callable(value) and value.__code__.co_argcount == 0:
            print(f"The value of {selected_variable} is: ")
            value()
        else:
            print(f"The value of {selected_variable} is: {value}")
    else:
        print(f"Variable {selected_variable} does not exist")


def inquire(files):
    # Get the list of files
    # files = list_files(smb_path, username, password, directory)
    if not files:
        print("No list provided to inquire about.")
        return

    # Ask the user to select files (multi-select)
    questions = [
        inquirer.Checkbox(
            "files",
            message="Select files to operate on",
            choices=files,
        ),
    ]

    prompt = inquirer.prompt(questions)
    if not prompt:
        print("Creating a prompt failed!")
        return

    selected_files = prompt["files"]

    if not selected_files:
        print("No options selected.")
        return
    return selected_files


def inquire_file_intend(selected_files, operation_map, saveTo=""):

    if len(selected_files) == 0:
        print("No Files to operate on, can't inquire about intend.")
        return False
    # create a keymappping of operational_name + lambda function executing on selected_file
    # Ask what to do with the selected files
    # operations = ["Download", "Delete"] #"Do nothing"]
    operation = inquirer.list_input(
        "What would you like to do?", choices=operation_map.keys()
    )

    try:

        for sel_file in selected_files:
            res = operation_map[operation](sel_file, saveTo)
            print("Res after executin lambda...")
            input(res)

        """
        if operation == "Download":
            for file in selected_files:
                # local_path = input(f"Enter the destination path for {file}: ")
                print(f"Download Stub for {file}.")
                # download_file(os.path.join(directory, file), local_path)
        elif operation == "Delete":
            for file in selected_files:
                print(f"Delete Stub for {file}.")
                # delete_file(os.path.join(directory, file))
        else:   
        """
    except Exception as e:
        print(f"Operation: {operation} failed to performed.")
        print(e)
        return False

    return True


def delete_file(smb_path, username, password, file_path):
    import smbclient

    smbclient.ClientConfig(username=username, password=password)

    try:
        smbclient.remove(file_path)
        print(f"File {file_path} has been successfully deleted.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")


def forever_acp(
    prompt_message, lookupTable, key="enter", is_password=False, bottom_toolbar=None
):
    while True:
        result = autocompleteprompt(
            prompt_message,
            lookupTable,
            key=key,
            is_password=is_password,
            bottom_toolbar=bottom_toolbar,
        )

        # Check if result is in lookupTable
        if result in lookupTable:
            return result  # Valid choice, exit loop and return result

        # Otherwise, keep looping until valid choice is made
        print("Invalid choice. Please select a valid option from the provided choices.")


def autocompleteprompt(
    prompt_message, lookupTable, key="enter", is_password=False, bottom_toolbar=None
):
    # Create a WordCompleter with the table names
    completer = WordCompleter(lookupTable, ignore_case=True)

    key_bindings = KeyBindings()
    # Add key binding for cycling through options with Tab key

    @key_bindings.add("tab")
    def _(event):
        event.current_buffer.complete_state = None  # Reset completion state.
        event.current_buffer.start_completion(select_first=True)

    # initial_text = ""
    # if lookupTable:
    #    # Pre-type the first letter of the first term
    #    initial_text = list(lookupTable)[0][0]

    # @key_bindings.add("tab")
    # def _(event):
    #     foundIndex = -1
    #     if len(event.current_buffer.text) == 1:
    #         for i, term in enumerate(lookupTable):
    #             if term.lower().startswith(event.current_buffer.text.lower()):
    #                 if i != len(lookupTable)-1:
    #                     foundIndex = i+1
    #                     continue
    #                 else:
    #                     event.current_buffer.text = list(lookupTable)[0]
    #                     break
    #             if foundIndex != -1:
    #                 event.current_buffer.text = term[:1]
    #                 foundIndex = -1
    #                 break
    #     else:
    #         event.current_buffer.complete_next()

    @key_bindings.add(key)
    def _(event):
        buffer_text = event.current_buffer.text
        if (
            buffer_text == "x"
            or buffer_text == "q"
            or buffer_text == ""
            or buffer_text is None
        ):
            key_bindings.remove(_)
            event.app.exit()
            return

        if not buffer_text.isdigit():
            key_bindings.remove(_)
            # return
        else:
            event.current_buffer.text = ""  # Reset if digit

        if buffer_text not in lookupTable:
            for term in lookupTable:
                if term.lower().startswith(buffer_text.lower()):
                    # Pre-type the first letter
                    event.current_buffer.text = term
                    # event.current_buffer.text = term[:1]
                    break

        if buffer_text not in lookupTable:
            event.current_buffer.complete_next()

    viMode = False
    return prompt(
        prompt_message,
        completer=completer,
        key_bindings=key_bindings,
        editing_mode=EditingMode.VI if viMode else EditingMode.EMACS,
        default="",  # initial_text,
        is_password=is_password,
        bottom_toolbar=bottom_toolbar,
    )


def autocompletepromptTuple(prompt_message, lookupTable, typeLookupTable, key="enter"):
    # Create a WordCompleter with the table names
    completer = WordCompleter(lookupTable, ignore_case=True)
    typeCompleter = WordCompleter(typeLookupTable, ignore_case=True)

    key_bindings = KeyBindings()

    @key_bindings.add(key)
    def _(event):
        buffer_text = event.current_buffer.text
        if (
            buffer_text == "x"
            or buffer_text == "q"
            or buffer_text == ""
            or buffer_text is None
        ):
            key_bindings.remove(_)
            event.app.exit()
            return

        if buffer_text not in lookupTable:
            for term in lookupTable:
                if term.lower().startswith(buffer_text.lower()):
                    event.current_buffer.insert_text(term[len(buffer_text) :] + " = ")
                    break
        elif buffer_text.endswith(" = "):
            event.current_buffer.start_completion(
                completer=typeCompleter, validate_while_typing=True
            )
        elif buffer_text.endswith(", "):
            event.current_buffer.start_completion(
                completer=completer, validate_while_typing=True
            )
        else:
            event.current_buffer.complete_next()

        key_bindings.remove(_)

    # Create key bindings for the current data

    viMode = False
    return prompt(
        prompt_message,
        completer=completer,
        key_bindings=key_bindings,
        editing_mode=EditingMode.VI if viMode else EditingMode.EMACS,
    )


def decorate_array_with_colorama(array):
    color_map = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "blue": Fore.BLUE,
        "yellow": Fore.YELLOW,
        "cyan": Fore.CYAN,
        "magenta": Fore.MAGENTA,
        "white": Fore.WHITE,
        "reset": Style.RESET_ALL,
    }

    decorated_elements = []
    for element in array:
        color = color_map.get(element)
        if color:
            decorated_elements.append(f"{color}{element}{Style.RESET_ALL}")
        else:
            decorated_elements.append(element)

    return decorated_elements


def arrToFormattedText(modes):
    formatted_text = []
    color_map = {
        "red": "class:red",
        "green": "class:green",
        "blue": "class:blue",
        "yellow": "class:yellow",
        "cyan": "class:cyan",
        "magenta": "class:magenta",
        "white": "class:white",
        "reset": "class:reset",
    }
    color_map_colorama = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "blue": Fore.BLUE,
        "yellow": Fore.YELLOW,
        "cyan": Fore.CYAN,
        "magenta": Fore.MAGENTA,
        "white": Fore.WHITE,
        "reset": Style.RESET_ALL,
    }

    for i, ele in enumerate(modes):
        if i == 0:
            formatted_text.append(("class:reset", ": ["))
        color = random.choice(list(color_map.values()))

        if i != len(modes) - 1:
            formatted_text.append((color, str(ele) + ", "))
        else:
            formatted_text.append((color, str(ele)))

        if i == len(modes) - 1:
            formatted_text.append(("class:reset", "]"))
    return FormattedText(formatted_text)


def convert_colorama_to_formatted_text(colorama_string):
    color_map = {
        "black": "class:black",
        "red": "class:red",
        "green": "class:green",
        "yellow": "class:yellow",
        "blue": "class:blue",
        "magenta": "class:magenta",
        "cyan": "class:cyan",
        "white": "class:white",
        "bright_black": "class:bright_black",
        "bright_red": "class:bright_red",
        "bright_green": "class:bright_green",
        "bright_yellow": "class:bright_yellow",
        "bright_blue": "class:bright_blue",
        "bright_magenta": "class:bright_magenta",
        "bright_cyan": "class:bright_cyan",
        "bright_white": "class:bright_white",
        "reset": "class:reset",
    }

    formatted_text = []
    parts = colorama_string.split("\033[")

    for part in parts:
        if "m" in part:
            color_code = part.split("m")[0]
            colors = color_code.split(";")
            text = part.split("m", 1)[1]

            color_tuples = []
            for color in colors:
                color = color_map.get(color)
                if color:
                    color_tuples.append((color, ""))

            formatted_text.extend(color_tuples)
            formatted_text.append(("class:reset", text))
        else:
            formatted_text.append(("class:reset", part))

    return FormattedText(formatted_text)


def paginated_display(df, start=0, page_size=10):
    num_rows = df.shape[0]
    end = min(page_size, num_rows)
    while start < num_rows:
        print(df.iloc[start:end])
        if end == num_rows:
            break
        user_input = input(
            f"Press {Fore.GREEN}Enter{Style.RESET_ALL}'to continue or enter '{Fore.RED}q{Style.RESET_ALL}'/'{Fore.RED}x{Style.RESET_ALL}' to break: "
        )
        if user_input.lower() == "q" or user_input.lower() == "x":
            break
        start = end
        end = min(end + page_size, num_rows)


def determine_indentation_type(lines):
    indentation_type = None
    threshold = 4  # Adjust this threshold based on your needs

    for line in lines:
        if line.strip():
            indentation = line[: len(line) - len(line.lstrip())]
            if len(indentation) >= threshold:
                indentation_type = indentation[0]
                break

    return indentation_type


def add_indentation(lines, indentation_type, level=2):
    indented_lines = []
    current_indentation = 0

    for line in lines:
        indentation = line[: len(line) - len(line.lstrip())]

        if "class" in line:
            level **= 2
            if indentation_type == "\t":
                indented_line = line.replace(" " * level, "\t")
            else:
                indented_line = line.replace("\t", " " * level)

            indented_lines.append("\t" * current_indentation + indented_line)
            level //= 2
            if "{" in line:
                level **= 2
            if "}" in line:
                level //= 2
            continue

        if "{" in line:
            level **= 2
        if "}" in line:
            level //= 2

        if indentation_type == "\t":
            indented_line = line.replace(" " * level, "\t")
        else:
            indented_line = line.replace("\t", " " * level)

        if indentation.startswith("\t"):
            current_indentation += 1
        elif indentation.startswith(" " * level):
            current_indentation -= 1

        indented_lines.append("\t" * current_indentation + indented_line)

    return indented_lines


if __name__ == "__main__":
    ret = checkbox_input("Example Title", ["A", "B", "C"])
    print(ret)

    """
    for i in range(10):
        print("Loading" + "." * i)
        sys.stdout.write("\033[F")  # Cursor up one line
        time.sleep(1)
    """
    # point by point
    """
    msg = "Loading"

    print(msg, end="")

    for _ in range(10):
        print(end=".")
        sys.stdout.flush()
        time.sleep(1)
    print()
    # Or all char by char
    i = 10
    msg = "Loading" + "." * i

    for char in msg:
        print(end=char)
        sys.stdout.flush()
        time.sleep(1 if char == "." else 0.1)
    print()
    """

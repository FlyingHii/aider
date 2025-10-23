import tempfile
from pathlib import Path

from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model
from aider.utils import ChdirTemporaryDirectory

def trigger_edit_file(
        file_name: str, original_content: str, search_content: str, replace_content: str
):
    """
    Triggers an edit operation on a specified file using a simulated edit block.

    Args:
        file_name (str): The name of the file to be edited.
        original_content (str): The initial content to write to the file.
        search_content (str): The content to search for in the file.
        replace_content (str): The content to replace the search_content with.
    """
    # Define a temporary directory to work in
    with ChdirTemporaryDirectory():
        # Create the temporary file with original_content
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(original_content)

        files = [file_name]

        # Initialize the Coder object with mocked IO and a simple model
        gpt35 = Model("gpt-3.5-turbo")
        io = InputOutput(yes=True)  # Auto-confirm changes
        coder = Coder.create(
            gpt35,
            "diff",
            io=io,
            fnames=files,
        )

        # Mock the send method to return our desired edit block
        def mock_send(*args, **kwargs):
            coder.partial_response_content = f"""
Do this:

{file_name}
<<<<<<< SEARCH
{search_content}
=======
{replace_content}
>>>>>>> REPLACE

"""
            coder.partial_response_function_call = dict()
            return []

        coder.send = mock_send

        # Call the run method to apply the edit
        print(
            f"Original content of {file_name}:\n{Path(file_name).read_text(encoding='utf-8')}"
        )
        print("Triggering edit...")
        coder.run(with_message="hi")

        # Verify the content of the file after the edit
        content = Path(file_name).read_text(encoding="utf-8")
        expected_content = original_content.replace(search_content, replace_content, 1)

        if content == expected_content:
            print(f"Successfully edited {file_name}. New content:\n{content}")
        else:
            print(f"Edit failed. Expected:\n{expected_content}\nGot:\n{content}")
            raise AssertionError("File content does not match expected after edit.")


if __name__ == "__main__":
    # Example usage:
    file_name = "example_file.txt"
    original_content = "line one\nline two\nline three\n"
    search_content = "line two"
    replace_content = "MODIFIED line two"

    trigger_edit_file(file_name, original_content, search_content, replace_content)

    print("\n--- Running another example ---")
    file_name_2 = "another_file.py"
    original_content_2 = "def func_a():\n    pass\n\ndef func_b():\n    print('hello')\n"
    search_content_2 = "pass"
    replace_content_2 = "    # Implement logic here"
    trigger_edit_file(file_name_2, original_content_2, search_content_2, replace_content_2)

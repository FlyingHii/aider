import tempfile
from pathlib import Path

from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model
from aider.utils import ChdirTemporaryDirectory


def trigger_edit_file():
    # Define a temporary directory to work in
    with ChdirTemporaryDirectory():
        # Create a temporary file
        temp_file_name = "test_file.txt"
        orig_content = "one\ntwo\nthree\n"

        with open(temp_file_name, "w", encoding="utf-8") as f:
            f.write(orig_content)

        files = [temp_file_name]

        # Initialize the Coder object with mocked IO and a simple model
        # Use a dummy model as we are mocking the send method
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
            # This is the edit block content that the "LLM" would return
            coder.partial_response_content = f"""
Do this:

{temp_file_name}
<<<<<<< SEARCH
two

from uniquebible import config
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import prompt

class NumberValidator(Validator):
    def validate(self, document):
        text = document.text

        if text.lower() == config.terminal_cancel_action:
            pass
        elif text and not text.isdigit():
            i = 0

            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message='This entry accepts numbers only!', cursor_position=i)

class NoAlphaValidator(Validator):
    def validate(self, document):
        text = document.text

        if text.lower() == config.terminal_cancel_action:
            pass
        elif text and text.isalpha():
            i = 0

            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if c.isalpha():
                    break

            raise ValidationError(message='This entry does not accept alphabet letters!', cursor_position=i)
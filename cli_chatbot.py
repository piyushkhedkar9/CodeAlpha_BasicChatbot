"""
cli_chatbot.py
---------------
Plain command-line version of the rule-based chatbot.

This is the simplest possible front end: it shows the core
input() / print() / while-loop pattern with no UI framework at all,
delegating all "thinking" to chatbot_logic.get_response().

Run it with:
    python cli_chatbot.py
"""

from chatbot_logic import get_response, is_exit_command

BANNER = """
==========================================
   RuleBot - Simple Rule-Based Chatbot
   Type 'bye', 'exit' or 'quit' to stop.
==========================================
"""


def main():
    print(BANNER)
    print("Bot: Hi! I'm RuleBot. Ask me something, or type 'help'.\n")

    while True:                              # main chat loop
        user_input = input("You: ")          # input

        bot_reply = get_response(user_input) # function call (backend logic)
        print(f"Bot: {bot_reply}")            # output

        if is_exit_command(user_input):       # loop exit condition
            break

    print("\n[Chat session ended]")


if __name__ == "__main__":
    main()

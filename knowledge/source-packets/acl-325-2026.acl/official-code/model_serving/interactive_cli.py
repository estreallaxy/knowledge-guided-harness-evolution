import argparse

from structured_tutor import TutorSession, add_backend_args, build_generator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Interactive CLI for ScaffoldLM tutoring with hidden planning and sub-question tracking."
    )
    add_backend_args(parser)
    parser.add_argument("--question", default="", help="Optional initial question. If omitted, read from stdin.")
    parser.add_argument("--show-plan", action="store_true", help="Print the internally generated plan.")
    return parser.parse_args()


def read_initial_question(args) -> str:
    if args.question.strip():
        return args.question.strip()
    print("Please enter the math question:")
    question = input("> ").strip()
    if not question:
        raise ValueError("Question cannot be empty.")
    return question


def main():
    args = parse_args()
    generate = build_generator(args)
    question = read_initial_question(args)

    session = TutorSession(question=question, generate=generate)
    first_reply = session.start()

    if args.show_plan:
        print("\n[Internal Plan]")
        print(session.subquestions_text)

    print("\nTutor:")
    print(first_reply)

    while not session.is_finished:
        try:
            user_input = input("\nStudent> ").strip()
        except EOFError:
            print("\nSession ended by EOF.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Session ended by user.")
            break

        reply = session.respond(user_input)
        print("\nTutor:")
        print(reply)

    if session.is_finished:
        print("\n[Session finished: the tutor reached an explicit end-of-session response.]")


if __name__ == "__main__":
    main()

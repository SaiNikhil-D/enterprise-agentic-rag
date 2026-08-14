from .sql_agent import sql_agent_node


questions = [

    "How many employees are in Engineering?",

    "How many employees are in HR?",

    "Who is the ML Engineer?",

    "Which employees work in Hyderabad?"

]


for question in questions:

    print("\n" + "=" * 70)

    print("QUESTION:")

    print(question)


    state = {

        "question": question

    }


    result = sql_agent_node(
        state
    )


    print("\nANSWER:")

    print(
        result["answer"]
    )
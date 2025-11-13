from agents import get_agent
from argparse import ArgumentParser
from events import TherapySession
from utils import load_json, get_model_client


CLIENTS = load_json("data/characters/clients.json")
CLIENTS = load_json("data/characters/Patient Psi CM Dataset.json")
THERAPISTS = load_json("data/characters/therapists.json")


if __name__ == "__main__":
    args = ArgumentParser()
    args.add_argument("--lang", type=str, default="en")
    args.add_argument("--client", type=str, default="patientPsi")
    args.add_argument("--therapist", type=str, default="user")
    args.add_argument("--eval_mode", type=str, default="cbt")
    args.add_argument("--max_turns", type=int, default=60)
    args.add_argument("--reminder_turn_num", type=int, default=5)
    args.add_argument("--api_type", type=str, default="LAB")
    args.add_argument("--model_name", type=str, default="gpt-4o")
    args.add_argument("--langfuse", action="store_true", default=False)
    # args.add_argument("--api_type", type=str, default="OR")
    # args.add_argument("--model_name", type=str, default="deepseek/deepseek-r1")

    args = args.parse_args()

    model_client = get_model_client(args.model_name, args.api_type)

    client = get_agent(
        "client", agent_type=args.client, model_client=model_client, data=CLIENTS[0]
    )
    therapist = get_agent(
        "therapist",
        agent_type=args.therapist,
        model_client=model_client,
        data=THERAPISTS[0],
    )
    # evaluator = get_agent(
    #     "evaluator",
    #     agent_type=args.eval_mode,
    #     model_client=model_client,
    # )

    session = TherapySession(
        client=client,
        therapist=therapist,
        evaluator=None,
        max_turns=args.max_turns,
        reminder_turn_num=args.reminder_turn_num,
        output_dir=f"data/sessions/{client.name}-{therapist.name}/session_1.json",
    )

    config = {"recursion_limit": 1000}
    if args.langfuse:
        from langfuse.langchain import CallbackHandler

        session_handler = CallbackHandler()
        config["callbacks"] = [session_handler]

    session.graph.invoke(
        input={},
        config=config,
    )

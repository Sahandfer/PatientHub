import os
from argparse import ArgumentParser
from agents.clients import get_client
from agents.therapists import get_therapist
from agents.evaluators import SkillEvaluator, GeneralEvaluator
from components.events import TherapySession
from utils import load_json, get_model_client
from langfuse.langchain import CallbackHandler

CLIENTS = load_json("data/characters/clients.json")
CLIENTS = load_json("data/characters/Patient Psi CM Dataset.json")
THERAPISTS = load_json("data/characters/therapists.json")


if __name__ == "__main__":
    args = ArgumentParser()
    args.add_argument("--client", type=str, default="patientPsi")
    args.add_argument("--mode", type=str, default="skill")
    args.add_argument("--therapist", type=str, default="user")
    args.add_argument("--max_turns", type=int, default=60)
    args.add_argument("--reminder_turn_num", type=int, default=5)
    args.add_argument("--api_type", type=str, default="LAB")
    args.add_argument("--model_name", type=str, default="gpt-4o")
    args.add_argument(
        "--roleplaydoh_verbose",
        action="store_true",
        help="Print Roleplay-doh pipeline steps when using roleplaydoh client.",
    )
    args.add_argument(
        "--roleplaydoh_log_file",
        type=str,
        default=None,
        help="Optional path to store Roleplay-doh pipeline logs (JSON lines).",
    )
    args = args.parse_args()
    # model_name = "deepseek/deepseek-r1"
    # api_type = "OR"
    # model_name = "qwen/qwen3-235b-a22b:free"
    # api_type = "OLLAMA"
    # model_name = "qwen3:14b"

    if args.roleplaydoh_verbose:
        os.environ["ROLEPLAYDOH_VERBOSE"] = "1"
    else:
        os.environ.pop("ROLEPLAYDOH_VERBOSE", None)
    if args.roleplaydoh_log_file:
        os.environ["ROLEPLAYDOH_LOG"] = args.roleplaydoh_log_file
    else:
        os.environ.pop("ROLEPLAYDOH_LOG", None)

    model_client = get_model_client(args.model_name, args.api_type)
    # session_handler = CallbackHandler()

    client = get_client(
        agent_type=args.client, model_client=model_client, data=CLIENTS[0]
    )
    therapist = get_therapist(
        agent_type=args.therapist, model_client=model_client, data=THERAPISTS[0]
    )
    if args.mode == "skill":
        critic = SkillEvaluator(model_client=model_client)
    elif args.mode == "cbt":
        critic = GeneralEvaluator(model_client=model_client)

    session = TherapySession(
        client=client,
        therapist=therapist,
        evaluator=critic,
        max_turns=args.max_turns,
        reminder_turn_num=args.reminder_turn_num,
        output_dir=f"data/sessions/{client.name}-{therapist.name}/session_1.json",
    )

    session.graph.invoke(
        input={},
        # config={"callbacks": [session_handler], "recursion_limit": 100},
        config={"recursion_limit": 1000},
    )

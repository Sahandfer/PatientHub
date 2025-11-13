from agents import get_agent
from argparse import ArgumentParser
from utils import load_json, get_model_client

if __name__ == "__main__":
    args = ArgumentParser()
    args.add_argument("--lang", type=str, default="en")
    args.add_argument("--api_type", type=str, default="LAB")
    args.add_argument("--model_name", type=str, default="gpt-4o")

import json
from dotenv import load_dotenv
from agents import BasicClient, BasicTherapist
from events import TherapySession

load_dotenv(".env")

CLIENTS = json.load(open("data/characters/clients.json"))
THERAPISTS = json.load(open("data/characters/therapists.json"))


if __name__ == "__main__":
    client = BasicClient("gpt-4o", CLIENTS[0])
    therapist = BasicTherapist("gpt-4o", THERAPISTS[0])
    session = TherapySession({"Client": client, "Therapist": therapist})

    session.simulate()

"""
An example for simulating a therapy session between a client and a therapist.
It requires:
    - A client agent
    - A therapist agent
    - (Optional) An evaluator agent
It creates a TherapySession object and runs the simulation using LangGraph.
The configurations for the session and agents are specified in the `configs/simulate.yaml` file.
"""

import hydra
from omegaconf import DictConfig

from src.events import TherapySession
from src.agents import get_inference_agent


@hydra.main(version_base=None, config_path="../configs", config_name="simulate")
def simulate(configs: DictConfig) -> None:
    lang = configs.session.lang
    # Load client
    configs.client.lang = lang
    client = get_inference_agent(category="client", configs=configs.client)

    # Load therapist
    configs.therapist.lang = lang
    therapist = get_inference_agent(category="therapist", configs=configs.therapist)

    # Load evaluator
    # configs.evaluator.lang = lang
    # evaluator = get_inference_agent(category="evaluator", configs=configs.evaluator)

    # Create therapy session
    session = TherapySession(
        client=client, therapist=therapist, evaluator=None, configs=configs.session
    )

    # Setting up langgraph
    lg_config = {"recursion_limit": configs.session.recursion_limit}
    if configs.session.langfuse:
        from langfuse.langchain import CallbackHandler

        session_handler = CallbackHandler()
        lg_config["callbacks"] = [session_handler]

    session.graph.invoke(
        input={},
        config=lg_config,
    )


if __name__ == "__main__":
    simulate()

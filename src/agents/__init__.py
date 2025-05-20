from agents.patient import BasicPatient, PatientPsi
from agents.therapist import BasicTherapist


def get_patient(agent_type):
    if agent_type == "basic":
        return BasicPatient
    if agent_type == "patient-psi":
        return PatientPsi
    else:
        print("Invalid agent type. ")
        return None


def get_therapist(agent_type):
    if agent_type == "basic":
        return BasicTherapist
    else:
        print("Invalid agent type. ")
        return None

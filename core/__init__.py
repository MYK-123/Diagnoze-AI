#!/bin/env python3

from auth.users import User
from core.symptoms_input import SymptomInputs, add_new_symptom_input


def symptom_list_from_input(from_input :str, user: User) -> SymptomInputs:
    # use NLP to identify list of symptoms from from_input

    # also save the query in database
    add_new_symptom_input(user.user_id, from_input)

    
    return SymptomInputs()

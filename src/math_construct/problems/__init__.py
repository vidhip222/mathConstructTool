import glob
import importlib
import os
import re
from .problem import Problem
import inspect

# Dictionary to store problem classes
problem_classes = {}

# Find all folders in the problems directory, don't include files or folders starting with _
g = os.path.join(os.path.dirname(__file__), "*")
problem_folders = glob.glob(g)
problem_folders = [folder for folder in problem_folders if os.path.isdir(folder) and not folder.split('/')[-1].startswith('_')]

for problem_folder in problem_folders:
    folder_name = os.path.basename(problem_folder)
    problem_files = glob.glob(os.path.join(problem_folder, "*.py"))
    curr_problems = {}
    for problem_file in problem_files:
        module_name = os.path.basename(problem_file)[:-3]  # Remove .py extension
        module = importlib.import_module(f".{module_name}", package=f"math_construct.problems.{folder_name}")
        
        # Find all Problem classes in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if attr_name == "Problem" or not (inspect.isclass(attr) and issubclass(attr, Problem)):
                continue
            assert isinstance(attr, type)
            curr_problems[attr.config.name] = attr
    if len(curr_problems) > 0:
        problem_classes[folder_name] = curr_problems

def get_problem_class(problem_name: str):
   problem_classes = get_all_problem_classes()
   for problem_class in problem_classes:
       if problem_class.config.name == problem_name:
           return problem_class
   return None

# Returns all flattened problem classes
def get_all_problem_classes(include_backups=False) -> list[type]:
    groups_sorted = sorted(list(problem_classes.items()), key=lambda kv: kv[0].lower())
    all_problem_classes = [] 
    for group, problems in groups_sorted:
        if group == "backups" and not include_backups:
            continue
        problems_sorted = sorted(list(problems.items()), key=lambda kv: kv[0].lower()) 
        all_problem_classes += [problem[1] for problem in problems_sorted]
    return all_problem_classes

group_info = {
    "backups": "Backup Problems",
    "bmo-shortlist": "Balkan Mathematical Olympiad (+Shortlists)",
    "bulgarian": "Bulgarian Competitions (National, MO, IFYM)",
    "croatian": "Croatian Competitions (MO)",
    "bxmo": "Benelux Mathematical Olympiad",
    "dutch": "Dutch Competitions (MO)",
    "emc": "European Mathematical Cup",
    "imc": "International Mathematics Competition for University Students",
    "imo-shortlist": "International Mathematical Olympiad (+Shortlists)",
    "jbmo-shortlist": "Junior Balkan Mathematical Olympiad (+Shortlists)",
    "konhauser": "Konhauser Problemfest",
    "misc": "Misc (Baltic/Flanders/Polish MO, IMO Prep Handouts, etc.)",
    "putnam": "William Lowell Putnam Mathematical Competition",
    "serbian": "Serbian Competitions (MO, IMO Team Selection Test, Regionals)",
    "swiss": "Swiss Competitions (MO, IMO Team Selection Test)",
    "tot": "Tournament of Towns",
    "usamo": "USA Mathematical Olympiad",
    "usamts": "USA Mathematical Talent Search"
}

# Returns the problem classes per group 
def get_problem_classes_per_group(include_backups=False) -> list[tuple[str, list[tuple[str, type]]]]:
    groups_sorted = sorted(list(problem_classes.items()), key=lambda kv: kv[0].lower())
    all_problem_classes = [] 
    for group, problems in groups_sorted:
        if group == "backups" and not include_backups:
            continue
        problems_sorted = sorted(list(problems.items()), key=lambda kv: kv[0].lower()) 
        all_problem_classes.append((group, problems_sorted))
    return all_problem_classes
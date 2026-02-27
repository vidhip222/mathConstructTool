from math_construct.problems import get_problem_classes_per_group, get_all_problem_classes, group_info
import argparse
from loguru import logger
from math_construct.problems.problem import Tag

argparser = argparse.ArgumentParser()
argparser.add_argument("--group", type=str, default=None)
argparser.add_argument("--problem", type=str, default=None)
argparser.add_argument("--exclude-formatting", action="store_true")

args = argparser.parse_args()

problem_classes_all = get_problem_classes_per_group()
problem_classes = []
for problem in problem_classes_all:
    if args.group is not None and problem[0] != args.group:
        continue
    if args.problem is not None and problem[1] != args.problem.config.name:
        continue
    problem_classes.append(problem)

with open('src/scripts/latex/exported_problems.tex', 'w') as f:
    # print summary table of size per group 
    f.write("\\begin{table}[h] \\centering \\begin{tabular}{rrl}\n")
    f.write("\\toprule\n")
    f.write("Source & \# & Source Description \\\\\n")
    f.write("\\midrule\n")
    for group, problems in problem_classes:
        group = group.replace('_', '-')
        f.write(f"{group} & {len(problems)} & {group_info[group]} \\\\\n")
    f.write("\\midrule\n")
    f.write("\\textbf{\\textsc{MathConstruct}} & \\textbf{" + str(len(get_all_problem_classes())) + "} \\\\\n")
    f.write("\\bottomrule \\end{tabular} \n")
    f.write("\\caption{Summary of \\textsc{MathConstruct} problems by source.}")
    f.write("\\label{tab:bench_cattype_summary}")
    f.write("\\end{table}\n")

    # print problem category X type table 
    cats = [Tag.COMBINATORICS, Tag.ALGEBRA, Tag.NUMBER_THEORY, Tag.GEOMETRY] #, Tag.PUZZLE]
    types = [Tag.FIND_ANY, Tag.FIND_ALL, Tag.FIND_INF, Tag.FIND_MAX_MIN]
    cat_type_stats = {cat: {typ: 0 for typ in types} for cat in cats}
    for group, problems in problem_classes:
        for problem_name, problem_class in problems:
            found_cats = 0
            found_types = 0
            for tag in problem_class.config.tags:
                if tag in cats:
                    found_cats += 1
                    for typ in problem_class.config.tags:
                        if typ in types:
                            found_types += 1
                            cat_type_stats[tag][typ] += 1
            if found_cats > 1:
                logger.warning(f"Problem {problem_name} has more than one category")
            if found_types > 1:
                logger.warning(f"Problem {problem_name} has more than one type")
            if found_cats == 0: 
                logger.warning(f"Problem {problem_name} has no category")
            if found_types == 0:
                logger.warning(f"Problem {problem_name} has no type")
    f.write("\\begin{table}[h] \\centering \\begin{tabular}{r" + "r"*len(types) + "r}\n")
    f.write("\\toprule\n")
    f.write("Category & " + " & ".join([str(typ.value).replace('_', ' ').replace('Infinitely ', 'Inf') for typ in types]) + " & Total\\\\\n")
    f.write("\\midrule\n")
    totals_per_cat = {}
    for cat in cats:
        totals_per_cat[cat] = sum([cat_type_stats[cat][typ] for typ in types])
        f.write(f"{cat.value} & " + " & ".join([str(cat_type_stats[cat][typ]) for typ in types]) + " & " + str(totals_per_cat[cat]) + " \\\\\n")
    f.write("\\midrule\n")
    totals_per_typ = {} 
    for typ in types:
        totals_per_typ[typ] = sum([cat_type_stats[cat][typ] for cat in cats])
    total = sum(totals_per_cat.values())
    assert total == sum(totals_per_typ.values())
    f.write("\\textbf{\\textsc{MathConstruct}} & " + " & ".join([str(totals_per_typ[typ]) for typ in types]) + " & " + str(total) + "\\\\\n")

    f.write("\\bottomrule \\end{tabular} \n")
    f.write("\\caption{Summary of \\textsc{MathConstruct} problems by category and type.}")
    f.write("\\label{tab:bench_summary}")
    f.write("\\end{table}\n")



    f.write("\\clearpage\n")

    for group, problems in problem_classes:
        f.write(f"\\subsection{{{group.replace('_', '-')}}}\n")
        for problem_name, problem_class in problems:
            f.write(f"\\subsubsection{{{problem_name}}} \\mbox{{}}\\\\\n")
            orig_problem = problem_class.get_original()
            f.write("\\textit{Source: " + orig_problem.config.source + "}\\\\\n")
            if orig_problem.config.problem_url is None or len(orig_problem.config.problem_url) < 10:
                logger.info(f"Problem {problem_name} has no problem URL")
            if orig_problem.config.solution_url is None or len(orig_problem.config.solution_url) < 10:
                logger.info(f"Problem {problem_name} has no solution URL")
            if orig_problem.config.tags is None or len(orig_problem.config.tags) == 0:
                logger.info(f"Problem {problem_name} has no tags")
            #f.write("\\textit{Problem URL: \\verbatim{" + orig_problem.config.problem_url + "} }\\\\\n")
            #if orig_problem.config.solution_url is not None:
            #    f.write("\\textit{Solution URL: \\verbatim{" + orig_problem.config.solution_url + "} }\\\\\n")
            #else:
            #    f.write("\\textit{Solution URL: /}\\\\\n")
            tags = ", ".join([str(x.value) for x in orig_problem.config.tags])
            f.write("\\textit{Tags: " + tags + "}\\\\\n")
            f.write(f"{orig_problem}\n\n")
            if not args.exclude_formatting:
                formatting_instructions = orig_problem.get_formatting()
                f.write(f"{formatting_instructions}\n")
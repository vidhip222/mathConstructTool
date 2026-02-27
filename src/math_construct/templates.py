from typing import Optional

MATRIX_FORMATTING_TEMPLATE = r"""Output the answer between \verb|\begin{array}{...}| and \verb|\end{array}| inside of $\boxed{...}$. For example, $\boxed{\begin{array}{ccc}1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 9\end{array}}$."""

LIST_FORMATTING_TEMPLATE = r"""Output the answer as a comma separated list inside of $\boxed{...}$. For example $\boxed{1, 2, 3}$."""

INTEGER_FORMATTING_TEMPLATE = r"""Output the answer as an integer inside of $\boxed{...}$. For example $\boxed{123}$."""

FRACTION_FORMATTING_TEMPLATE = r"""Output the answer as a fraction inside of $\boxed{...}$. For example $\boxed{\frac{1}{2}}$."""

def get_matrix_template(extra_instructions: Optional[str] = None) -> str:
    ret = MATRIX_FORMATTING_TEMPLATE
    if extra_instructions is not None:
        ret += f"\n{extra_instructions}"
    return ret
 

def get_list_template(extra_instructions: Optional[str] = None) -> str:
    ret = LIST_FORMATTING_TEMPLATE
    if extra_instructions is not None:
        ret += f"\n{extra_instructions}"
    return ret


def get_integer_template(extra_instructions: Optional[str] = None) -> str:
    ret = INTEGER_FORMATTING_TEMPLATE
    if extra_instructions is not None:
        ret += f"\n{extra_instructions}"
    return ret


def get_fraction_template(extra_instructions: Optional[str] = None) -> str:
    ret = FRACTION_FORMATTING_TEMPLATE
    if extra_instructions is not None:
        ret += f"\n{extra_instructions}"
    return ret

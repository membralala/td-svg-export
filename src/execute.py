import pathlib


def onCreate():
    default_dir = pathlib.Path().resolve()
    default_name = parent.svg.name
    for par in parent.svg.pars():
        if par.name == "Directory":
            par.default = default_dir
            if not par.eval():
                par.val = default_dir
        if par.name == "Filename":
            par.default = default_name
            if not par.eval():
                par.val = default_name

    # activate for build
    # parent.svg.showCustomOnly = True

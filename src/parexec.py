FORMATS = {"Letter": (279.4, 279.4), "A4": (210, 297), "Custom": "Custom"}


def onValueChange(par, prev):
    # redirect general value changes
    general_cases = dict(
        Format=onFormatChange,
    )

    if par.name in general_cases:
        general_cases[par.name](par, prev)
        return

    # redirect layer specific value changes
    layer_cases = dict(
        Rendermode=onRendermodeChange,
        Position=onPositionChange,
    )

    case_type = "".join(filter(lambda x: not x.isdigit(), par.name))
    if case_type in layer_cases:
        layerId = int("".join(filter(lambda x: x.isdigit(), par.name)))
        layer_cases[case_type](par, prev, layerId)


def onPulse(par):
    # redirect general pulses
    general_cases = dict(
        Savesvg=onSavesvg,
        Addsop=onAddsop,
    )

    if par.name in general_cases:
        general_cases[par.name](par)
        return

    # redirect layer specific pulses
    layer_cases = dict(
        Remove=onRemove,
    )

    case_type = "".join(filter(lambda x: not x.isdigit(), par.name))
    if case_type in layer_cases:
        layerId = int("".join(filter(lambda x: x.isdigit(), par.name)))
        layer_cases[case_type](par, layerId)


def onSavesvg(par):
    overflow = parent.svg.par.Overflow
    parent.svg.Save(allow_canvas_overflow=overflow)


def onAddsop(par):
    layer = parent.svg.AddLayer()
    createGUIElem(layer)


def onRemove(par, layerId):
    sel = ui.messageBox(
        "",
        f"Are you sure, that you want to delete Layer(ID:{layerId})?",
        buttons=["Yes", "No"],
    )
    if sel == 0:
        layer = parent.svg.RemoveLayer(layerId)
        destroyGUIElem(layer)


def onFormatChange(par, prev) -> None:
    format = FORMATS[str(par)]
    sizex, sizey = parent.svg.par.Sizex, parent.svg.par.Sizey
    if format == "Custom":
        sizex.val, sizey.val = parent.svg.GetCustomsize()
        sizex.enable = True
    else:
        sizex.val, sizey.val = format
        sizex.enable = False


def onRendermodeChange(par, prev, layerId: int) -> None:
    layer = parent.svg.GetLayer(layerId)
    updateRendermode(layer, par)


def onPositionChange(par, prev, layerId: int) -> None:
    layers = parent.svg.AllLayers()
    layer = layers.pop(int(prev))
    layers.insert(int(par), layer)
    page = parent.svg.customPages[0]
    for l in layers:
        context = l.pars
        parameter_data = dict(
            zip(
                [elem.name for elem in context], [elem.val for elem in context]
            )
        )
        destroyGUIElem(l)
        createGUIElem(l)

        for elem in page:
            if elem.name in parameter_data:
                elem.val = parameter_data[elem.name]

        updateRendermode(l)


def createGUIElem(layer) -> None:
    """Create GUI parameters for a specified layer."""

    page = parent.svg.customPages[0]

    header = page.appendHeader(
        f"Header{layer.layerId}", label=f"SOP (ID:{layer.layerId})"
    )
    header[0].startSection = True

    page.appendMenu(f"Position{layer.layerId}", label="Position")
    for l in parent.svg.AllLayers():
        position = l.parsDict["Position"]
        position.menuNames = [i for i in range(len(parent.svg.AllLayers()))]
        position.menuLabels = [i for i in range(len(parent.svg.AllLayers()))]
        position.val = parent.svg.AllLayers().index(l)

    page.appendSOP(f"Sop{layer.layerId}", label=f"SOP")

    page.appendXY(f"Offset{layer.layerId}", label=f"Offset")

    rendermode = page.appendMenu(
        f"Rendermode{layer.layerId}", label=f"Render Mode"
    )
    rendermode[0].menuNames = ["Lines", "Pgons", "All"]
    rendermode[0].menuLabels = [
        "Polylines",
        "Polygons",
        "Polylines and Polygons",
    ]
    rendermode[0].val = "Lines"

    strokewidth = page.appendFloat(
        f"Strokewidth{layer.layerId}", label="Strokewidth"
    )
    strokewidth[0].normMin = 0
    strokewidth[0].normMax = 10
    strokewidth[0].default = 1
    strokewidth[0].val = 1

    linecolor = page.appendRGBA(
        f"Linecolor{layer.layerId}", label=f"Line Color"
    )
    linecolor[3].val = 1

    pgoncolor = page.appendRGBA(
        f"Polycolor{layer.layerId}", label=f"Polygon Color"
    )
    pgoncolor[0].val = 1
    pgoncolor[1].val = 1
    pgoncolor[2].val = 1
    pgoncolor[3].val = 1
    pgoncolor[0].enable = False

    page.appendPulse(f"Remove{layer.layerId}", label=f"Remove SOP")


def destroyGUIElem(layer) -> dict:
    """Delete a layer's GUI parameters."""

    names = [
        "Header",
        "Sop",
        "Position",
        "Offset",
        "Linecolor",
        "Polycolor",
        "Rendermode",
        "Remove",
        "Strokewidth",
    ]
    parameters = dict()

    page = parent.svg.customPages[0]
    for name in names:
        for elem in page:
            if elem.name.startswith(f"{name}{layer.layerId}"):
                parameters[elem.name] = elem.val
                elem.destroy()
    return parameters


def updateRendermode(layer, rendermode: str = None) -> None:
    """Update the GUI for a specified layer based on the item
    selection of Rendermode.
    """

    parsDict = layer.parsDict
    polycolor = parsDict["Polycolorr"]
    linecolor = parsDict["Linecolorr"]
    strokewidth = parsDict["Strokewidth"]

    if not rendermode:
        rendermode = parsDict["Rendermode"]

    if rendermode == "Lines":
        strokewidth.enable = True
        linecolor.enable = True
        polycolor.enable = False
    elif rendermode == "Pgons":
        strokewidth.enable = False
        linecolor.enable = False
        polycolor.enable = True
    else:
        strokewidth.enable = True
        linecolor.enable = True
        polycolor.enable = True

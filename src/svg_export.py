import svgwrite


class OutOfCanvasException(Exception):
    pass


class Layer:
    """
    A single layer handling the sop-to-svg pipeline.

    The layer object will specify a unique identifier, that is used
    to generate its dedicated GUI parameters. Its main purpose is then
    to find and handle those GUI parameters as well as their state.
    """

    _LAYER_ID = 0

    def __init__(self, layerId: int = None) -> None:
        if not layerId:
            self._layerId = type(self)._LAYER_ID
            type(self)._LAYER_ID += 1
        else:
            self._layerId = layerId
            # prevent overwriting, when SOPs are not ordered numerical
            type(self)._LAYER_ID = max(layerId, type(self)._LAYER_ID) + 1

    def __repr__(self) -> str:
        return f"{type(self).__name__}(ID:{self.layerId})"

    @property
    def layerId(self) -> int:
        return self._layerId

    @layerId.setter
    def layerId(self, new):
        raise AttributeError("layerId is a read-only parameter!")

    @property
    def pars(self) -> list:
        pars = parent.svg.pars(f"*{self.layerId}*")
        for par in pars.copy():
            if par.page != "Layer":
                pars.remove(par)
        return pars

    @property
    def parsDict(self) -> dict:
        pars = self.pars
        layerIdAsString = str(self.layerId)
        names = (par.name.replace(layerIdAsString, "") for par in pars)
        return dict(zip(names, pars))

    @property
    def SCALAR(self) -> float:
        return 2.835

    def write(
        self,
        dwg: svgwrite.Drawing,
        sizex: float,
        sizey: float,
        allow_canvas_overflow: bool = True,
    ) -> bool:
        """Write a SOP to a ~svgwrite.Drawing instance.

        Returns ~True on success, ~False otherwise.
        """

        scalar = self.SCALAR
        parsDict = self.parsDict
        offx = parsDict["Offsetx"]
        offy = parsDict["Offsety"]
        linecolor = (
            parsDict["Linecolorr"],
            parsDict["Linecolorg"],
            parsDict["Linecolorb"],
            parsDict["Linecolora"],
        )
        pgoncolor = (
            parsDict["Polycolorr"],
            parsDict["Polycolorg"],
            parsDict["Polycolorb"],
            parsDict["Polycolora"],
        )
        strokewidth = parsDict["Strokewidth"]
        rendermode = parsDict["Rendermode"]

        sop = op(parsDict["Sop"])
        if not sop:
            return False

        prims = sop.prims

        for item in prims:
            newPoints = [
                (vert.point.x + offx, sizey - (vert.point.y + offy))
                for vert in item
            ]

            if not allow_canvas_overflow:
                for point in newPoints:
                    x, y = point
                    if not (0 <= x <= sizex and 0 <= y <= sizey):
                        raise OutOfCanvasException(
                            f"The SOP of {self} is out of the bounds of"
                            "the defined canvas size.\n"
                        )

            # Scale points, so that size=1 in TD equals to size=1mm
            newPoints = [(x * scalar, y * scalar) for x, y in newPoints]

            if not rendermode == "Pgons":
                dwg.add(
                    dwg.polyline(
                        points=newPoints,
                        stroke=self.stringify_color(linecolor),
                        stroke_width=strokewidth.eval(),
                        fill="none",
                    )
                )
            if not rendermode == "Lines":
                dwg.add(
                    dwg.polygon(
                        points=newPoints,
                        stroke="none",
                        stroke_width=0,
                        fill=self.stringify_color(pgoncolor),
                    )
                )

        return True

    def stringify_color(self, rgba: tuple) -> str:
        r, g, b, a = rgba
        r *= 255
        g *= 255
        b *= 255
        return (
            f"rgb({int(r) & 255}, {int(g) & 255}, {int(b) & 255})"
            if a
            else "none"
        )


class SvgExport:
    """Export svg files from within TouchDesigner rendering
    polygons and polylines.
    """

    def __init__(self) -> None:
        self.customsize = (1000, 1000)
        self.layers = []

        page = parent.svg.customPages[0]
        for elem in page:
            if elem.name.startswith("Header"):
                layerId = int(elem.name[6:])
                self.layers.append(Layer(layerId=layerId))

    @property
    def canvassize(self) -> tuple:
        return float(parent.svg.par.Sizex), float(parent.svg.par.Sizey)

    def GetCustomsize(self) -> tuple:
        return self.customsize

    def SetCustomsize(self, x: int, y: int) -> None:
        self.customsize = x, y

    def Save(
        self,
        filename: str = None,
        layerId: int = None,
        allow_canvas_overflow=True,
    ) -> str:
        sizex, sizey = self.canvassize
        dwg = svgwrite.Drawing(
            size=(str(sizex) + "mm", str(sizey) + "mm"),
            profile="tiny",
        )

        try:
            if layerId:
                layer = self.GetLayer(layerId=layerId)
                success = layer.write(
                    dwg,
                    sizex,
                    sizey,
                    allow_canvas_overflow=allow_canvas_overflow,
                )
            else:
                success = False
                for layer in reversed(self.layers):
                    success = (
                        layer.write(
                            dwg,
                            sizex,
                            sizey,
                            allow_canvas_overflow=allow_canvas_overflow,
                        )
                        or success
                    )
        except OutOfCanvasException as e:
            choice = ui.messageBox(
                "Warning",
                str(e) + "Do you still want to continue?",
                buttons=["No", "Yes"],
            )
            if choice == 0:
                return

        if not filename:
            # Check, if directory and filename are set
            dir = parent.svg.par.Directory
            name = parent.svg.par.Filename
            if dir and name:
                filename = f"{dir}/{name}.svg"
            else:
                ui.messageBox(
                    "Warning", "Please set a Directory and a Filename first."
                )
                return

        dwg.saveas(filename=filename)
        return filename

    def AddLayer(self) -> Layer:
        """Append a new ~Layer instance to ~self.layers."""

        layer = Layer()
        self.layers.append(layer)
        return layer

    def RemoveLayer(self, layerId: int) -> Layer:
        """Remove a ~Layer instance from ~self.layers."""

        layer = self.GetLayer(layerId)
        self.layers.remove(layer)
        return layer

    def GetLayer(self, layerId: int) -> Layer:
        """Find a ~Layer instance in ~self.layers."""
        if not isinstance(layerId, int):
            raise TypeError(f"layerId must be int, not {type(layerId)}")

        for layer in self.layers:
            if layer.layerId == layerId:
                return layer

    def AllLayers(self) -> list:
        """Return ~self.layers."""

        return self.layers

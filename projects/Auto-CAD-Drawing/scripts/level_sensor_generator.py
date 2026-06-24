#!/usr/bin/env python3
"""Generate DONJUN level-sensor CAD sheets as editable DXF files."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ezdxf
from ezdxf.enums import TextEntityAlignment


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "data" / "cpx26051_sensors.json"
DEVICE_MODELS_PATH = ROOT / "data" / "device_models.json"
OUTPUT_DIR = ROOT / "output" / "cpx26051"

PAPER_SIZES = {
    "A3_LANDSCAPE": (420.0, 297.0),
    "A4_PORTRAIT": (210.0, 297.0),
}


@dataclass(frozen=True)
class Sheet:
    config: dict[str, Any]
    sensors: list[dict[str, Any]]


class CadCanvas:
    def __init__(self, doc: ezdxf.EzDxfDocument, width: float, height: float) -> None:
        self.doc = doc
        self.msp = doc.modelspace()
        self.width = width
        self.height = height

    def line(self, x1: float, y1: float, x2: float, y2: float, layer: str = "WIRE") -> None:
        self.msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})

    def rect(self, x: float, y: float, w: float, h: float, layer: str = "BORDER") -> None:
        self.msp.add_lwpolyline(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)],
            dxfattribs={"layer": layer},
        )

    def circle(self, x: float, y: float, r: float, layer: str = "SYMBOL") -> None:
        self.msp.add_circle((x, y), r, dxfattribs={"layer": layer})

    def text(
        self,
        value: Any,
        x: float,
        y: float,
        size: float = 2.5,
        layer: str = "TEXT_CN",
        align: str = "center",
        rotation: float = 0.0,
        style: str = "CN",
    ) -> None:
        if value is None:
            return
        value = str(value)
        if not value:
            return
        alignment = {
            "left": TextEntityAlignment.MIDDLE_LEFT,
            "center": TextEntityAlignment.MIDDLE_CENTER,
            "right": TextEntityAlignment.MIDDLE_RIGHT,
        }[align]
        entity = self.msp.add_text(
            value,
            dxfattribs={
                "height": size,
                "layer": layer,
                "style": style,
                "rotation": rotation,
            },
        )
        entity.set_placement((x, y), align=alignment)

    def mtext(
        self,
        value: str,
        x: float,
        y: float,
        size: float = 2.5,
        width: float = 50,
        layer: str = "TEXT_CN",
        align: int = 5,
    ) -> None:
        if not value:
            return
        entity = self.msp.add_mtext(
            value,
            dxfattribs={
                "char_height": size,
                "width": width,
                "layer": layer,
                "style": "CN",
                "attachment_point": align,
            },
        )
        entity.set_location((x, y))


def load_data(data_path: Path = DEFAULT_DATA_PATH) -> dict[str, Any]:
    return json.loads(data_path.read_text(encoding="utf-8"))


def load_device_models(path: Path = DEVICE_MODELS_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_level_sensor_project(data: dict[str, Any], device_models: dict[str, Any] | None = None) -> list[str]:
    device_models = device_models or load_device_models()
    generator = data.get("generator", {})
    messages: list[str] = []

    if generator.get("type") != "level_sensor":
        raise ValueError(f"unsupported generator type: {generator.get('type')!r}")

    models = sorted({sensor["model"] for sensor in data.get("sensors", [])})
    unsupported = [model for model in models if model not in device_models]
    if unsupported:
        raise ValueError(f"unsupported sensor model(s): {', '.join(unsupported)}")
    messages.append(f"sensor model library ok: {', '.join(models)}")

    required_sensor_fields = {"lt_tag", "tank_cn", "tank_en", "measurement", "install_type", "model", "terminal_pair", "cable"}
    for sensor in data.get("sensors", []):
        missing = sorted(required_sensor_fields - sensor.keys())
        if missing:
            raise ValueError(f"{sensor.get('lt_tag', '<unknown>')} missing field(s): {', '.join(missing)}")
        model = device_models[sensor["model"]]
        variants = model.get("variants", {})
        if sensor["install_type"] not in variants:
            raise ValueError(
                f"{sensor['lt_tag']} install type {sensor['install_type']!r} is not defined for {sensor['model']}"
            )
    messages.append("sensor records ok for level-sensor template")

    for sheet in data.get("sheets", []):
        if sheet.get("drawing_kind") not in {"circuit", "overview"}:
            raise ValueError(f"{sheet.get('output_name')} has unsupported drawing kind: {sheet.get('drawing_kind')}")
    messages.append("sheet templates ok: circuit/overview")
    return messages


def create_doc() -> ezdxf.EzDxfDocument:
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4  # millimeters

    layers = {
        "BORDER": 7,
        "TITLE_BLOCK": 7,
        "WIRE": 7,
        "TERMINAL": 7,
        "SYMBOL": 7,
        "TEXT_CN": 7,
        "TEXT_EN": 8,
        "REFERENCE": 9,
        "CHECK": 3,
    }
    for name, color in layers.items():
        if name not in doc.layers:
            doc.layers.new(name, dxfattribs={"color": color})

    if "CN" not in doc.styles:
        doc.styles.new("CN", dxfattribs={"font": "Arial Unicode.ttf"})
    if "EN" not in doc.styles:
        doc.styles.new("EN", dxfattribs={"font": "txt.shx"})
    return doc


def draw_arrow(canvas: CadCanvas, x: float, y: float, direction: str = "right") -> None:
    canvas.line(x - 4, y, x + 4, y, "WIRE")
    if direction == "right":
        pts = [(x + 4, y), (x + 1.5, y + 1.4), (x + 1.5, y - 1.4), (x + 4, y)]
    elif direction == "left":
        pts = [(x - 4, y), (x - 1.5, y + 1.4), (x - 1.5, y - 1.4), (x - 4, y)]
    else:
        pts = [(x, y + 4), (x - 1.4, y + 1.5), (x + 1.4, y + 1.5), (x, y + 4)]
    canvas.msp.add_lwpolyline(pts, dxfattribs={"layer": "WIRE"})


def draw_ground(canvas: CadCanvas, x: float, y: float) -> None:
    canvas.line(x, y + 4, x, y, "SYMBOL")
    canvas.line(x - 4, y, x + 4, y, "SYMBOL")
    canvas.line(x - 3, y - 1.6, x + 3, y - 1.6, "SYMBOL")
    canvas.line(x - 2, y - 3.0, x + 2, y - 3.0, "SYMBOL")


def draw_frame(canvas: CadCanvas, meta: dict[str, Any], sheet: dict[str, Any]) -> None:
    width, height = canvas.width, canvas.height
    canvas.rect(5, 5, width - 10, height - 10, "BORDER")

    if width > 300:
        top_y = height - 10
        canvas.line(5, top_y, width - 5, top_y, "BORDER")
        for i in range(11):
            x = 5 + i * (width - 10) / 10
            canvas.line(x, top_y, x, height - 5, "BORDER")
            canvas.line(x, 5, x, 10, "BORDER")
            if i < 10:
                canvas.text(i + 1, x + (width - 10) / 20, height - 7.5, 2.2, "REFERENCE")
                canvas.text(i + 1, x + (width - 10) / 20, 7.5, 2.2, "REFERENCE")
        for idx, letter in enumerate("ABCDEF"):
            y = height - 17 - idx * 48
            canvas.text(letter, 3.0, y, 2.3, "REFERENCE")
            canvas.text(letter, width - 3.0, y, 2.3, "REFERENCE")
        canvas.text("+49 (0)2173 - 39 64 - 0", 25, height - 7, 2.1, "REFERENCE", "left")
        canvas.text("Monheim am Rhein", width - 80, height - 7, 2.1, "REFERENCE", "left")

    draw_title_block(canvas, meta, sheet)


def draw_title_block(canvas: CadCanvas, meta: dict[str, Any], sheet: dict[str, Any]) -> None:
    width = canvas.width
    if width > 300:
        x0, y0, w, h = 115.0, 5.0, width - 120.0, 35.0
        cols = [0, 28, 65, 91, 155, 250, 270, 285, w]
        pos = {
            "serial_label": x0 + 12,
            "project": x0 + 46,
            "vessel_label": x0 + 78,
            "vessel": x0 + 123,
            "system": x0 + 202,
            "version_label": x0 + 260,
            "version": x0 + 278,
            "scale_label": x0 + 292,
            "designer_label": x0 + 12,
            "designer": x0 + 46,
            "drawing_no_label": x0 + 78,
            "drawing_no": x0 + 123,
            "total_label": x0 + 260,
            "total": x0 + 278,
            "current_label": x0 + 292,
            "current": x0 + 292,
            "approver_label": x0 + 12,
            "approver": x0 + 46,
            "drawing_label": x0 + 78,
            "drawing_name": x0 + 123,
            "company_a": x0 + 205,
            "company_b": x0 + 258,
        }
        company_size = 3.5
    else:
        x0, y0, w, h = 5.0, 5.0, width - 10.0, 40.0
        cols = [0, 25, 55, 80, 135, 158, 178, w]
        pos = {
            "serial_label": x0 + 11,
            "project": x0 + 40,
            "vessel_label": x0 + 67,
            "vessel": x0 + 106,
            "system": x0 + 150,
            "version_label": x0 + 146,
            "version": x0 + 166,
            "scale_label": x0 + 187,
            "designer_label": x0 + 11,
            "designer": x0 + 40,
            "drawing_no_label": x0 + 67,
            "drawing_no": x0 + 106,
            "total_label": x0 + 146,
            "total": x0 + 166,
            "current_label": x0 + 187,
            "current": x0 + 198,
            "approver_label": x0 + 11,
            "approver": x0 + 40,
            "drawing_label": x0 + 67,
            "drawing_name": x0 + 106,
            "company_a": x0 + 128,
            "company_b": x0 + 165,
        }
        company_size = 2.4

    canvas.rect(x0, y0, w, h, "TITLE_BLOCK")
    for dy in (10, 20, 30):
        canvas.line(x0, y0 + dy, x0 + w, y0 + dy, "TITLE_BLOCK")

    for cx in cols[1:-1]:
        canvas.line(x0 + cx, y0, x0 + cx, y0 + h, "TITLE_BLOCK")

    drawing_kind = sheet.get("drawing_kind", "circuit")
    if drawing_kind == "overview":
        drawing_no = meta["drawing_no_overview"]
        name_cn = meta["drawing_name_overview_cn"]
        name_en = meta["drawing_name_overview_en"]
    else:
        drawing_no = meta["drawing_no_circuit"]
        name_cn = meta["drawing_name_circuit_cn"]
        name_en = meta["drawing_name_circuit_en"]

    canvas.text("项目编号/Serial No.", pos["serial_label"], y0 + 26, 1.8, "TEXT_CN")
    canvas.text(meta["project_id"], pos["project"], y0 + 25, 2.3, "TEXT_CN")
    canvas.text("船型/Vessel", pos["vessel_label"], y0 + 26, 1.8, "TEXT_CN")
    canvas.text(meta["vessel_cn"], pos["vessel"], y0 + 27, 2.2, "TEXT_CN")
    canvas.text(meta["vessel_en"], pos["vessel"], y0 + 23, 1.9, "TEXT_EN", style="EN")

    canvas.text(meta["system_cn"], pos["system"], y0 + 26, 2.4, "TEXT_CN")
    canvas.text(meta["system_en"], pos["system"], y0 + 21, 1.9, "TEXT_EN", style="EN")

    canvas.text("版本/Version", pos["version_label"], y0 + 26, 1.6, "TEXT_CN")
    canvas.text(meta["version"], pos["version"], y0 + 25, 2.4, "TEXT_CN")
    canvas.text("比例/Scale", pos["scale_label"], y0 + 26, 1.6, "TEXT_CN")

    canvas.text("设计/Designer", pos["designer_label"], y0 + 16, 1.8, "TEXT_CN")
    canvas.text(meta["designer"], pos["designer"], y0 + 15, 2.3, "TEXT_CN")
    canvas.text("图号/Drawing No.", pos["drawing_no_label"], y0 + 16, 1.8, "TEXT_CN")
    canvas.text(drawing_no, pos["drawing_no"], y0 + 15, 2.2, "TEXT_CN")
    canvas.text("总页数/Total Page", pos["total_label"], y0 + 16, 1.6, "TEXT_CN")
    canvas.text(meta["total_page"], pos["total"], y0 + 15, 2.3, "TEXT_CN")
    canvas.text("本页/Current P.", pos["current_label"], y0 + 16, 1.6, "TEXT_CN")
    canvas.text(sheet.get("current_page", ""), pos["current"], y0 + 15, 2.3, "TEXT_CN")

    canvas.text("审核/Approver", pos["approver_label"], y0 + 6, 1.8, "TEXT_CN")
    canvas.text(meta["approver"], pos["approver"], y0 + 5, 2.3, "TEXT_CN")
    canvas.text("图名/Drawing", pos["drawing_label"], y0 + 6, 1.8, "TEXT_CN")
    canvas.text(name_cn, pos["drawing_name"], y0 + 8, 2.0, "TEXT_CN")
    canvas.text(name_en, pos["drawing_name"], y0 + 4, 1.6, "TEXT_EN", style="EN")
    canvas.text("DONJUN", pos["company_a"], y0 + 5, company_size + 2.5, "TITLE_BLOCK", style="EN")
    canvas.text(meta["company"].replace("DONJUN ", ""), pos["company_b"], y0 + 5, company_size, "TITLE_BLOCK", style="EN")


def draw_junction_box(canvas: CadCanvas, x: float, y: float) -> None:
    canvas.rect(x - 12, y - 6, 24, 12, "SYMBOL")
    canvas.text("+接线盒", x - 15, y + 3.5, 2.2, "TEXT_CN", "right")
    canvas.text("J.B.", x, y - 1, 2.4, "TEXT_EN", style="EN")
    canvas.circle(x - 4, y, 0.9, "TERMINAL")
    canvas.circle(x + 4, y, 0.9, "TERMINAL")
    canvas.text("1", x - 4, y - 4, 1.9, "TERMINAL")
    canvas.text("2", x + 4, y - 4, 1.9, "TERMINAL")


def draw_sensor_box(canvas: CadCanvas, sensor: dict[str, Any], x: float, y: float) -> None:
    display_tag = sensor.get("display_tag", sensor["lt_tag"])
    canvas.text("-" + display_tag, x - 17, y + 8, 2.5, "TEXT_CN")
    canvas.rect(x - 10, y - 4, 20, 14, "SYMBOL")
    canvas.text("+", x - 4, y + 6, 2.0, "TEXT_CN")
    canvas.text("-", x + 4, y + 6, 2.0, "TEXT_CN")
    canvas.text("4~20mA", x, y + 1, 2.3, "TEXT_EN", style="EN")
    canvas.text(sensor["tank_cn"], x, y - 12, 2.4, "TEXT_CN")
    canvas.text(sensor["tank_en"], x, y - 18, 2.2, "TEXT_EN", style="EN")


def draw_lf701(canvas: CadCanvas, x: float, y: float) -> None:
    canvas.rect(x - 12, y - 14, 24, 28, "SYMBOL")
    canvas.text("LF701", x, y + 2, 2.4, "TEXT_EN", style="EN")
    for idx, dx in enumerate([-6, 0, 6], start=1):
        canvas.circle(x + dx, y + 9, 0.9, "TERMINAL")
        canvas.text(idx, x + dx, y + 6, 1.8, "TERMINAL")
    for idx, dx in enumerate([-6, 0, 6], start=4):
        canvas.circle(x + dx, y - 9, 0.9, "TERMINAL")
        canvas.text(idx, x + dx, y - 12, 1.8, "TERMINAL")
    canvas.text("GND", x + 15, y + 9, 1.8, "TERMINAL")


def draw_channel(canvas: CadCanvas, sensor: dict[str, Any], x: float, y_sensor: float) -> None:
    y_bus = 252
    y_tb = 232
    y_jb = 148
    y_cable = 200
    left_wire = x - 4
    right_wire = x + 4
    t1, t2 = sensor["terminal_pair"]

    canvas.text(sensor.get("top_ref", ""), x, 270, 2.1, "REFERENCE")
    draw_arrow(canvas, x, 263, "up")
    canvas.line(left_wire, y_bus, left_wire, y_tb + 4, "WIRE")
    canvas.line(right_wire, y_bus, right_wire, y_tb + 4, "WIRE")
    canvas.circle(left_wire, y_tb + 4, 0.8, "TERMINAL")
    canvas.circle(right_wire, y_tb + 4, 0.8, "TERMINAL")
    canvas.text(t1, left_wire - 1.5, y_tb + 1, 1.8, "TERMINAL")
    canvas.text(t2, right_wire + 1.5, y_tb + 1, 1.8, "TERMINAL")
    canvas.line(left_wire, y_tb, left_wire, y_jb + 6, "WIRE")
    canvas.line(right_wire, y_tb, right_wire, y_jb + 6, "WIRE")

    canvas.line(x - 13, y_tb - 6, x - 3, y_tb - 6, "SYMBOL")
    canvas.line(x - 13, y_tb - 8, x - 3, y_tb - 8, "SYMBOL")
    draw_ground(canvas, x + 12, y_tb - 14)
    canvas.text("Shield grounding", x + 20, y_tb - 10, 1.9, "TEXT_EN", "left", style="EN")

    canvas.text("-" + sensor["cable"], x - 14, y_cable + 5, 2.3, "TEXT_EN", style="EN")
    canvas.text("1x2x0.75", x - 14, y_cable, 2.2, "TEXT_EN", style="EN")
    canvas.line(x - 22, y_cable - 2, x + 18, y_cable - 2, "WIRE")

    # Cable break symbol
    canvas.line(left_wire, 190, x, 184, "SYMBOL")
    canvas.line(x, 184, left_wire, 178, "SYMBOL")
    canvas.line(right_wire, 190, x, 184, "SYMBOL")
    canvas.line(x, 184, right_wire, 178, "SYMBOL")

    draw_junction_box(canvas, x, y_jb)
    canvas.text("机带电缆", x, y_jb - 14, 2.2, "TEXT_CN")
    canvas.text("with cable", x, y_jb - 19, 2.0, "TEXT_EN", style="EN")

    y_after_jb = y_sensor + 12
    if sensor.get("barrier"):
        canvas.line(left_wire, y_jb - 6, left_wire, 112, "WIRE")
        canvas.line(right_wire, y_jb - 6, right_wire, 112, "WIRE")
        draw_lf701(canvas, x, 106)
        canvas.line(left_wire, 92, left_wire, y_after_jb, "WIRE")
        canvas.line(right_wire, 92, right_wire, y_after_jb, "WIRE")
    else:
        canvas.line(left_wire, y_jb - 6, left_wire, y_after_jb, "WIRE")
        canvas.line(right_wire, y_jb - 6, right_wire, y_after_jb, "WIRE")

    draw_sensor_box(canvas, sensor, x, y_sensor)


def draw_circuit_sheet(canvas: CadCanvas, meta: dict[str, Any], sheet: Sheet) -> None:
    draw_frame(canvas, meta, sheet.config)
    width = canvas.width
    y_bus = 252
    y_tb = 232
    y_sensor = 76
    terminal_strip = sheet.config.get("terminal_strip", "TB1")
    canvas.line(25, y_bus, width - 35, y_bus, "WIRE")
    draw_arrow(canvas, 30, y_bus, "left")
    draw_arrow(canvas, width - 40, y_bus, "right")
    canvas.text(sheet.config.get("bus_left_label", ""), 18, y_bus, 2.1, "REFERENCE", "left")
    canvas.text(sheet.config.get("bus_right_label", ""), width - 36, y_bus, 2.1, "REFERENCE", "left")
    canvas.line(5, y_tb, width - 5, y_tb, "REFERENCE")
    canvas.text(terminal_strip, 64, y_tb + 2, 2.2, "REFERENCE")

    x_start = 75 if len(sheet.sensors) > 6 else 80
    x_end = 338 if len(sheet.sensors) > 6 else 245
    step = (x_end - x_start) / max(1, len(sheet.sensors) - 1)

    # Sensor boundary, matching the dashed equipment area in the reference.
    boundary_x = 48
    boundary_w = max(280, x_end - x_start + 65)
    canvas.rect(boundary_x, 52, boundary_w, 42, "REFERENCE")
    canvas.text("+液位传感器", boundary_x - 6, 88, 2.4, "TEXT_CN", "right")

    for idx, sensor in enumerate(sheet.sensors):
        draw_channel(canvas, sensor, x_start + idx * step, y_sensor)


def draw_overview(canvas: CadCanvas, meta: dict[str, Any], sheet: Sheet) -> None:
    draw_frame(canvas, meta, sheet.config)
    width, height = canvas.width, canvas.height

    canvas.text("布置区域 / Location: 集控室 / Engine Control Room", 12, height - 18, 2.5, "TEXT_CN", "left")
    canvas.text("液位系统数据采集箱", 105, height - 34, 3.0, "TEXT_CN")
    canvas.text("Level Data Acquisition Box", 105, height - 40, 2.4, "TEXT_EN", style="EN")
    canvas.rect(50, 72, 110, 160, "SYMBOL")
    canvas.rect(60, 182, 90, 36, "SYMBOL")
    canvas.text("网络交换机", 105, 204, 2.6, "TEXT_CN")
    canvas.text("Network switch", 105, 198, 2.2, "TEXT_EN", style="EN")
    canvas.text("TB1", 57, 168, 2.3, "REFERENCE", "left")

    x0 = 65
    for i in range(24):
        row = i % 12
        col = i // 12
        x = x0 + col * 42
        y = 160 - row * 6.5
        canvas.rect(x, y, 6, 4, "TERMINAL")
        canvas.text(2 * i + 1, x + 1.5, y + 2, 1.4, "TERMINAL")
        canvas.text(2 * i + 2, x + 4.5, y + 2, 1.4, "TERMINAL")

    # External power and communications.
    canvas.rect(18, 238, 55, 15, "SYMBOL")
    canvas.text("主电源输入", 45, 246, 2.2, "TEXT_CN")
    canvas.text("Main power supply", 45, 241, 1.9, "TEXT_EN", style="EN")
    canvas.line(73, 245, 135, 245, "WIRE")
    canvas.rect(18, 260, 55, 15, "SYMBOL")
    canvas.text("备用电源输入", 45, 268, 2.2, "TEXT_CN")
    canvas.text("Standby power supply", 45, 263, 1.9, "TEXT_EN", style="EN")
    canvas.line(73, 267, 135, 267, "WIRE")
    canvas.line(105, 182, 105, 155, "WIRE")
    canvas.text("以太网/通讯线 <100m", 112, 170, 2.0, "TEXT_CN", "left")

    # Sensor fan-out list.
    canvas.text("液位传感器 / Level sensors", 105, 64, 2.5, "TEXT_CN")
    sensors = sheet.sensors
    for i, sensor in enumerate(sensors):
        x = 18 + (i % 3) * 62
        y = 56 - (i // 3) * 5.2
        canvas.text(f"{sensor['lt_tag']} {sensor['tank_cn']}", x, y, 1.7, "TEXT_CN", "left")


def get_sheet(data: dict[str, Any], sheet_config: dict[str, Any]) -> Sheet:
    sensor_by_tag = {sensor["lt_tag"]: sensor for sensor in data["sensors"]}
    return Sheet(sheet_config, [sensor_by_tag[tag] for tag in sheet_config["lt_tags"]])


def render_proof(dxf_path: Path, png_path: Path, pdf_path: Path) -> tuple[bool, str]:
    try:
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import Frontend, RenderContext
        from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    except Exception as exc:  # pragma: no cover - depends on local optional deps
        return False, f"proof rendering skipped: {exc}"

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    fig = plt.figure(figsize=(16, 11), dpi=180)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    config = Configuration(
        color_policy=ColorPolicy.BLACK,
        background_policy=BackgroundPolicy.WHITE,
        min_lineweight=0.25,
    )
    try:
        Frontend(ctx, out, config=config).draw_layout(msp, finalize=True)
        ax.set_aspect("equal", adjustable="datalim")
        fig.savefig(png_path, dpi=180, facecolor="white")
        fig.savefig(pdf_path)
    finally:
        plt.close(fig)
    return True, "proof rendered"


def generate(
    selected: set[str] | None = None,
    proof: bool = True,
    output_dir: Path = OUTPUT_DIR,
    data_path: Path = DEFAULT_DATA_PATH,
) -> list[Path]:
    data = load_data(data_path)
    validate_level_sensor_project(data)
    meta = data["metadata"]
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    for sheet_config in data["sheets"]:
        output_name = sheet_config["output_name"]
        if selected and output_name not in selected:
            continue
        width, height = PAPER_SIZES[sheet_config["paper"]]
        doc = create_doc()
        canvas = CadCanvas(doc, width, height)
        sheet = get_sheet(data, sheet_config)
        if sheet_config["drawing_kind"] == "overview":
            draw_overview(canvas, meta, sheet)
        else:
            draw_circuit_sheet(canvas, meta, sheet)
        out_path = output_dir / f"{output_name}.dxf"
        doc.saveas(out_path)
        generated.append(out_path)
        print(f"wrote {out_path}")
        if proof:
            png_path = output_dir / f"{output_name}.png"
            pdf_path = output_dir / f"{output_name}.pdf"
            ok, message = render_proof(out_path, png_path, pdf_path)
            if ok:
                print(f"wrote {png_path}")
                print(f"wrote {pdf_path}")
            else:
                print(message)
    return generated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Normalized level-sensor project JSON data file.",
    )
    parser.add_argument(
        "--only",
        action="append",
        help="Generate only this output stem, e.g. DJC-26051-04-01-page-15. Can be passed more than once.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for generated DXF and proof files.",
    )
    parser.add_argument("--no-proof", action="store_true", help="Skip PNG/PDF proof rendering.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = set(args.only) if args.only else None
    generate(selected=selected, proof=not args.no_proof, output_dir=args.output_dir, data_path=args.data)


if __name__ == "__main__":
    main()

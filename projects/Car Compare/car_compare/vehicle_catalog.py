from __future__ import annotations

from typing import Any


MAKE_ALIASES = {
    "acura": "Acura",
    "alfa romeo": "Alfa Romeo",
    "aston martin": "Aston Martin",
    "audi": "Audi",
    "bentley": "Bentley",
    "benz": "Mercedes-Benz",
    "bmw": "BMW",
    "buick": "Buick",
    "cadillac": "Cadillac",
    "chevrolet": "Chevrolet",
    "chev": "Chevrolet",
    "chevy": "Chevrolet",
    "chrysler": "Chrysler",
    "dodge": "Dodge",
    "ferrari": "Ferrari",
    "fiat": "FIAT",
    "ford": "Ford",
    "genesis": "Genesis",
    "gmc": "GMC",
    "honda": "Honda",
    "hyundai": "Hyundai",
    "infiniti": "INFINITI",
    "jaguar": "Jaguar",
    "jeep": "Jeep",
    "kia": "Kia",
    "land rover": "Land Rover",
    "landrover": "Land Rover",
    "lamborghini": "Lamborghini",
    "lexus": "Lexus",
    "lincoln": "Lincoln",
    "lucid": "Lucid",
    "maserati": "Maserati",
    "mclaren": "McLaren",
    "mazda": "Mazda",
    "mercedes": "Mercedes-Benz",
    "mercedes benz": "Mercedes-Benz",
    "mercedes-benz": "Mercedes-Benz",
    "mercedesbenz": "Mercedes-Benz",
    "mini": "MINI",
    "mitsubishi": "Mitsubishi",
    "nissan": "Nissan",
    "polestar": "Polestar",
    "porsche": "Porsche",
    "ram": "RAM",
    "ram truck": "RAM",
    "ram trucks": "RAM",
    "rivian": "Rivian",
    "rolls": "Rolls-Royce",
    "rolls royce": "Rolls-Royce",
    "rolls-royce": "Rolls-Royce",
    "subaru": "Subaru",
    "tesla": "Tesla",
    "toyota": "Toyota",
    "vin fast": "VinFast",
    "vinfast": "VinFast",
    "volvo": "Volvo",
    "volkswagen": "Volkswagen",
    "vw": "Volkswagen",
}


MODEL_CATALOG = {
    "Acura": ["MDX", "RDX", "Integra", "TLX", "ZDX", "ADX", "NSX"],
    "Alfa Romeo": ["Stelvio", "Giulia", "Tonale", "4C"],
    "Aston Martin": ["DBX", "Vantage", "DB12", "DB11", "Vanquish"],
    "Audi": ["Q3", "Q4 e-tron", "Q5", "Q7", "Q8", "A3", "A4", "A5", "A6", "A7", "A8", "e-tron", "SQ5", "RS 6"],
    "Bentley": [
        "Continental GT",
        "Continental GTC",
        "Continental",
        "Bentayga",
        "Flying Spur",
        "Mulsanne",
    ],
    "BMW": [
        "M4",
        "M3",
        "M2",
        "M5",
        "X5",
        "X6",
        "X7",
        "4 Series",
        "3 Series",
        "440",
        "430",
        "340",
        "330",
    ],
    "Buick": ["Encore GX", "Envision", "Enclave", "Envista"],
    "Cadillac": ["Escalade", "Escalade IQ", "XT4", "XT5", "XT6", "CT4", "CT5", "Lyriq", "Optiq", "Vistiq"],
    "Chevrolet": ["Silverado 1500", "Silverado", "Equinox", "Tahoe", "Suburban", "Traverse", "Trax", "Corvette", "Malibu", "Blazer", "Colorado"],
    "Chrysler": ["Pacifica", "Voyager", "300"],
    "Dodge": ["Charger", "Challenger", "Durango", "Hornet"],
    "Ferrari": ["Roma", "296", "SF90", "Purosangue", "812", "F8"],
    "FIAT": ["500e", "500X", "124 Spider"],
    "Ford": ["F-150", "F-250", "F-350", "Explorer", "Escape", "Bronco", "Bronco Sport", "Mustang", "Maverick", "Expedition", "Ranger", "Edge"],
    "Genesis": ["GV60", "GV70", "GV80", "G70", "G80", "G90"],
    "GMC": ["Sierra", "Yukon", "Terrain", "Acadia", "Canyon", "Hummer EV"],
    "Honda": ["Civic", "Accord", "CR-V", "Passport", "Pilot", "Odyssey"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Palisade", "Venue", "Kona", "Ioniq 5", "Ioniq 6", "Ioniq 9", "Santa Cruz"],
    "INFINITI": ["QX50", "QX55", "QX60", "QX80", "Q50"],
    "Jaguar": ["F-Pace", "E-Pace", "I-Pace", "XF", "F-Type"],
    "Jeep": ["Grand Cherokee", "Wrangler", "Compass", "Gladiator", "Wagoneer", "Grand Wagoneer", "Cherokee", "Renegade"],
    "Kia": ["Sportage", "Telluride", "Sorento", "Seltos", "Carnival", "K5", "K4", "Soul", "Niro", "EV6", "EV9"],
    "Lamborghini": ["Urus", "Huracan", "Revuelto", "Temerario", "Aventador"],
    "Land Rover": ["Range Rover Sport", "Range Rover Velar", "Range Rover Evoque", "Range Rover", "Defender", "Discovery Sport", "Discovery"],
    "Lexus": ["LC", "LS", "LX", "RX", "GX", "IS", "ES", "NX", "TX", "RC"],
    "Lincoln": ["Navigator", "Aviator", "Nautilus", "Corsair"],
    "Lucid": ["Air", "Gravity"],
    "Maserati": ["Grecale", "Levante", "Ghibli", "Quattroporte", "GranTurismo", "MC20"],
    "Mazda": ["CX-5", "CX-50", "CX-30", "CX-90", "CX-70", "Mazda3", "MX-5 Miata"],
    "McLaren": ["GT", "Artura", "720S", "750S", "765LT"],
    "Mercedes-Benz": [
        "C-Class",
        "E-Class",
        "S-Class",
        "G-Class",
        "GLA",
        "GLB",
        "GLC",
        "GLE",
        "GLS",
        "AMG GT",
        "SL",
        "CLA",
        "CLE",
    ],
    "MINI": ["Cooper", "Countryman", "Clubman"],
    "Mitsubishi": ["Outlander", "Outlander Sport", "Eclipse Cross", "Mirage"],
    "Nissan": ["Rogue", "Altima", "Sentra", "Pathfinder", "Frontier", "Armada", "Murano", "Kicks", "Leaf", "Ariya", "Z"],
    "Polestar": ["2", "3", "4"],
    "Porsche": ["Cayenne", "911", "Panamera", "Macan", "Taycan", "718"],
    "RAM": ["1500", "2500", "3500", "ProMaster"],
    "Rivian": ["R1S", "R1T", "EDV"],
    "Rolls-Royce": ["Cullinan", "Ghost", "Phantom", "Spectre", "Wraith", "Dawn"],
    "Subaru": ["Outback", "Forester", "Crosstrek", "Ascent", "Impreza", "Legacy", "WRX", "BRZ", "Solterra"],
    "Tesla": ["Model Y", "Model 3", "Model S", "Model X", "Cybertruck"],
    "Toyota": ["Camry", "Corolla", "RAV4", "Tacoma", "Tundra", "4Runner", "Sienna", "Crown"],
    "VinFast": ["VF 6", "VF 7", "VF 8", "VF 9"],
    "Volkswagen": ["Atlas", "Atlas Cross Sport", "Tiguan", "Jetta", "Taos", "Golf", "ID 4", "Arteon"],
    "Volvo": ["XC90", "XC60", "XC40", "S60", "S90", "V60", "V90", "EX30", "EX90", "C40"],
}


MODEL_MAKE_HINTS = {
    "4runner": "Toyota",
    "718": "Porsche",
    "911": "Porsche",
    "accord": "Honda",
    "altima": "Nissan",
    "atlas": "Volkswagen",
    "bronco": "Ford",
    "camry": "Toyota",
    "cayenne": "Porsche",
    "civic": "Honda",
    "corvette": "Chevrolet",
    "corolla": "Toyota",
    "crosstrek": "Subaru",
    "crown": "Toyota",
    "cr-v": "Honda",
    "defender": "Land Rover",
    "elantra": "Hyundai",
    "enclave": "Buick",
    "escalade": "Cadillac",
    "explorer": "Ford",
    "f-150": "Ford",
    "forester": "Subaru",
    "frontier": "Nissan",
    "grand": "Jeep",
    "gv70": "Genesis",
    "gv80": "Genesis",
    "k5": "Kia",
    "macan": "Porsche",
    "m3": "BMW",
    "m4": "BMW",
    "mdx": "Acura",
    "mustang": "Ford",
    "outback": "Subaru",
    "pilot": "Honda",
    "range": "Land Rover",
    "rav4": "Toyota",
    "r1s": "Rivian",
    "r1t": "Rivian",
    "rogue": "Nissan",
    "sierra": "GMC",
    "sienna": "Toyota",
    "silverado": "Chevrolet",
    "sportage": "Kia",
    "tahoe": "Chevrolet",
    "tacoma": "Toyota",
    "taycan": "Porsche",
    "telluride": "Kia",
    "tiguan": "Volkswagen",
    "tundra": "Toyota",
    "wrangler": "Jeep",
    "xc60": "Volvo",
    "xc90": "Volvo",
    "yukon": "GMC",
    "lc": "Lexus",
    "ls": "Lexus",
    "lx": "Lexus",
    "rx": "Lexus",
    "gx": "Lexus",
    "nx": "Lexus",
    "tx": "Lexus",
}


TOKEN_DISPLAY = {
    "awd": "AWD",
    "cs": "CS",
    "csl": "CSL",
    "ev": "EV",
    "ex": "EX",
    "gt": "GT",
    "gtc": "GTC",
    "gts": "GTS",
    "gt3": "GT3",
    "gt4": "GT4",
    "gt63": "GT63",
    "4xe": "4xe",
    "lc": "LC",
    "ls": "LS",
    "lx": "LX",
    "m": "M",
    "m2": "M2",
    "m3": "M3",
    "m4": "M4",
    "m5": "M5",
    "m8": "M8",
    "amg": "AMG",
    "c": "C",
    "cla": "CLA",
    "cle": "CLE",
    "e": "E",
    "g": "G",
    "gla": "GLA",
    "glb": "GLB",
    "glc": "GLC",
    "gle": "GLE",
    "gls": "GLS",
    "maybach": "Maybach",
    "phev": "PHEV",
    "rwd": "RWD",
    "s": "S",
    "sl": "SL",
    "xdrive": "xDrive",
    "xse": "XSE",
    "xle": "XLE",
    "se": "SE",
    "le": "LE",
    "limited": "Limited",
    "lt": "LT",
    "f": "F",
    "i": "i",
    "denali": "Denali",
    "rubicon": "Rubicon",
    "trd": "TRD",
    "sel": "SEL",
    "sx": "SX",
    "xt": "XT",
    "4matic": "4MATIC",
    "4s": "4S",
    "cr-v": "CR-V",
    "hr-v": "HR-V",
    "cx-30": "CX-30",
    "cx-5": "CX-5",
    "cx-50": "CX-50",
    "cx-70": "CX-70",
    "cx-90": "CX-90",
    "f-150": "F-150",
    "f-250": "F-250",
    "f-350": "F-350",
    "gv60": "GV60",
    "gv70": "GV70",
    "gv80": "GV80",
    "q3": "Q3",
    "q5": "Q5",
    "q7": "Q7",
    "q8": "Q8",
    "qx50": "QX50",
    "qx55": "QX55",
    "qx60": "QX60",
    "qx80": "QX80",
    "r1s": "R1S",
    "r1t": "R1T",
    "vf": "VF",
    "wrx": "WRX",
    "xc40": "XC40",
    "xc60": "XC60",
    "xc90": "XC90",
}


MERCEDES_CLASS_LETTERS = {
    "C-Class": "C",
    "E-Class": "E",
    "S-Class": "S",
    "G-Class": "G",
}


SOURCE_MODEL_OVERRIDES: dict[tuple[str, str], dict[str, Any]] = {
    ("Bentley", "Continental GT"): {
        "model_aliases": ["Continental GT", "Continental"],
        "required_keywords": ["Bentley", "Continental", "GT"],
        "exclude_keywords": ["GTC", "Bentayga", "Flying Spur", "Mulsanne"],
        "autotrader_model": "Continental",
        "autotrader_path_segments": ["Bentley", "Continental", "GT"],
        "autotrader_notes": [
            "Autotrader often treats Continental as the model and GT as a trim/path segment.",
            "If the page falls back to all Bentley results, collect only rows with separate Continental and GT tokens.",
        ],
    },
    ("Bentley", "Continental GTC"): {
        "model_aliases": ["Continental GTC", "Continental"],
        "required_keywords": ["Bentley", "Continental", "GTC"],
        "exclude_keywords": ["Bentayga", "Flying Spur", "Mulsanne"],
        "autotrader_model": "Continental",
        "autotrader_path_segments": ["Bentley", "Continental", "GTC"],
        "autotrader_notes": [
            "Autotrader often treats Continental as the model and GTC as a trim/path segment.",
        ],
    },
}


def make_candidates() -> list[tuple[list[str], str]]:
    pairs = []
    for alias, canonical in MAKE_ALIASES.items():
        pairs.append((alias.split(), canonical))
    return sorted(pairs, key=lambda item: len(item[0]), reverse=True)


def model_candidates(make: str) -> list[tuple[list[str], str]]:
    pairs = []
    for model in MODEL_CATALOG.get(make, []):
        pairs.append((model.lower().split(), model))
    if make == "Mercedes-Benz":
        pairs.extend(
            [
                (["c"], "C-Class"),
                (["e"], "E-Class"),
                (["s"], "S-Class"),
                (["g"], "G-Class"),
            ]
        )
    return sorted(pairs, key=lambda item: len(item[0]), reverse=True)


def display_token(token: str) -> str:
    lowered = token.lower()
    if lowered in TOKEN_DISPLAY:
        return TOKEN_DISPLAY[lowered]
    if token.isdigit():
        return token
    if lowered.startswith("x") and lowered[1:].isdigit():
        return lowered.upper()
    return token[:1].upper() + token[1:]


def source_query_model(make: str, model: str, trim: str, source: str = "generic") -> str:
    override = SOURCE_MODEL_OVERRIDES.get((make, model), {})
    source_model = override.get(f"{source}_model")
    if isinstance(source_model, str):
        return source_model
    if source == "visor":
        return model
    first_trim = trim.split()[:1]
    if make == "Lexus" and model in {"LC", "LS", "LX", "RX", "GX", "NX", "TX", "IS", "ES", "RC"} and trim.split()[:1] and trim.split()[0].isdigit():
        return f"{model} {trim.split()[0]}"
    return model


def source_model_contains_trim(model_query: str, trim: str) -> bool:
    first_trim = trim.split()[:1]
    if not first_trim:
        return False
    return first_trim[0].lower() in model_query.lower().split()


def source_model_profile(make: str, model: str, trim: str, source: str = "generic") -> dict[str, Any]:
    override = SOURCE_MODEL_OVERRIDES.get((make, model), {})
    source_model = source_query_model(make, model, trim, source)
    trim_tokens = [display_token(token) for token in trim.split() if token]
    if override.get("required_keywords"):
        required = list(override["required_keywords"])
    elif make == "Mercedes-Benz" and model in MERCEDES_CLASS_LETTERS:
        required = [make, MERCEDES_CLASS_LETTERS[model]]
    else:
        required = [make, *model.replace("-", " ").split()]
    for token in trim_tokens:
        if token not in required:
            required.append(token)
    path_segments = override.get(f"{source}_path_segments")
    if not path_segments:
        path_segments = [make, source_model]
    notes = list(override.get(f"{source}_notes") or [])
    return {
        "canonical_model": model,
        "source_model": source_model,
        "model_aliases": list(override.get("model_aliases") or [model]),
        "required_keywords": required,
        "exclude_keywords": list(override.get("exclude_keywords") or []),
        "path_segments": list(path_segments),
        "notes": notes,
    }

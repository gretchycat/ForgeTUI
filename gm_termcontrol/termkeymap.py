def gen_keymap():
    term_keymap = {
        # --- Manual Standard Overrides ---
        "\x7f":"Backspace",
        "\x1b":"Esc",
        "\x00":"Ctrl  ",
        "\x09":"Tab", 
        "\x0a":"Enter", 
        "\x0d":"Enter", 
        "\x1b[Z":"Shift Tab",
        "\x1b\n":"Alt Enter",
    }

    special = {28: "\\", 29: "] 5", 30: "^ 6", 31: "/ 7"}
    # --- 1. C0 Control Codes (Ctrl+A to Ctrl+Z) ---
    for i in range(1, 32):
        # Handle the Information Separators
        char = special.get(i, chr(i + 64))
        if term_keymap.get(chr(i)) is None:
            term_keymap[chr(i)] = f"Ctrl {char}"

    # --- 2. XTerm Modified Sequences ---
    modifiers = {
        "2": "Shift", "3": "Alt", "4": "Shift Alt", "5": "Ctrl",
        "6": "Ctrl Shift", "7": "Ctrl Alt", "8": "Ctrl Shift Alt",
        "9": "Meta", "10": "Meta Shift", "12": "Meta Shift Alt",
        "13": "Meta Ctrl","14": "Meta Ctrl Shift","15": "Meta Ctrl Alt",
        "16": "Meta Ctrl Shift Alt",

    }

    # CSI Suffixes (1;modX)
    nav_f_codes = {
        "A": "Up", "B": "Down", "C": "Right", "D": "Left", 
        "H": "Home", "F": "End", "P": "F1", "Q": "F2", "R": "F3", "S": "F4"
    }

    # Tilde Codes (code;mod~)
    tilde_codes = {
        "2": "Ins", "3": "Del", "5": "PgUp", "6": "PgDn",
        "15": "F5", "17": "F6", "18": "F7", "19": "F8", 
        "20": "F9", "21": "F10", "23": "F11", "24": "F12",
        "32": "SysRq", "34": "Break",
    }

    #keys with no modifiers
    for code, name in nav_f_codes.items():
        term_keymap[f"\x1bO{code}"] = f"{name}"
        term_keymap[f"\x1b[{code}"] = f"{name}"
    for code, name in tilde_codes.items():
        term_keymap[f"\x1b[{code}~"] = f"{name}"

    #keys for all the modifiers
    for mod_val, mod_name in modifiers.items():
        for code, name in nav_f_codes.items():
            term_keymap[f"\x1b[1;{mod_val}{code}"] = f"{mod_name} {name}"
        for code, name in tilde_codes.items():
            term_keymap[f"\x1b[{code};{mod_val}~"] = f"{mod_name} {name}"

    # --- 3. Alt + Keys (Meta) ---
    for i in range(32, 127): # Space through ~
        term_keymap[f"\x1b{chr(i)}"] = f"Alt {chr(i)}"

    return term_keymap

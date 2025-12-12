# prompt_templates.py
#
# Usage (zero-shot):
#   from prompt_templates import PROMPTS
#   tmpl = PROMPTS["RandomPosition"]["zero_shot"]
#   prompt = tmpl.format(LOG_TEXT=log_text)
#
# Usage (few-shot):
#   few_block = "...your few-shot examples text..."
#   tmpl = PROMPTS["RandomPosition"]["few_shot"]
#   prompt = tmpl.format(FEW_SHOT_EXAMPLES=few_block, LOG_TEXT=log_text)

PROMPTS = {
    # 1) DoS
    "DoS": {
        "zero_shot": (
            "You are detecting ATTACK vs GENUINE behaviour in V2X logs.\n\n"
            "Attack type: DoS (denial-of-service).\n"
            "In a DoS-style attack, a sender may behave abnormally and flood the network with messages "
            "that are not consistent with realistic driving or safety needs.\n\n"
            "Definitions:\n"
            "- \"attack\": this log record comes from a sender that is behaving in a way that looks abnormal "
            "  or suspicious for the scenario (e.g., excessive, redundant, or clearly unusual messages).\n"
            "- \"genuine\": this log record comes from a sender whose state and behaviour look like normal traffic.\n\n"
            "You will be given one log record in natural language.\n"
            "Decide if it is ATTACK or GENUINE.\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Log:\n"
            "{LOG_TEXT}\n\n"
            "Answer:"
        ),
        "few_shot": (
            "You are detecting ATTACK vs GENUINE behaviour in V2X logs.\n\n"
            "Attack type: DoS (denial-of-service).\n\n"
            "Below are labeled examples of log records and whether they are attack or genuine. "
            "After the examples, classify a new log record.\n\n"
            "Examples:\n"
            "{FEW_SHOT_EXAMPLES}\n\n"
            "Now classify the following log record:\n"
            "{LOG_TEXT}\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Answer:"
        ),
    },

    # 2) FakeEBLJustAttack
    "FakeEBLJustAttack": {
        "zero_shot": (
            "You are analyzing V2X logs for FAKE EEBL (Emergency Electronic Brake Light) misbehavior.\n\n"
            "Some vehicles may send EEBL-related messages or warnings that do NOT match realistic braking "
            "behaviour (FakeEBLJustAttack), while genuine vehicles either behave normally or send warnings "
            "only when braking hard in a plausible way.\n\n"
            "Definitions:\n"
            "- \"attack\": the sender's EEBL-related behaviour looks suspicious or inconsistent with its motion "
            "  and distance (e.g., frequent warnings without real braking).\n"
            "- \"genuine\": the sender behaves like a normal vehicle, with realistic EEBL behaviour.\n\n"
            "You will be given a short description of one sender's motion, distances, and warnings.\n"
            "Decide if it is ATTACK or GENUINE.\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Log:\n"
            "{LOG_TEXT}\n\n"
            "Answer:"
        ),
        "few_shot": (
            "You are analyzing V2X logs for FAKE EEBL misbehavior (FakeEBLJustAttack).\n\n"
            "Below are labeled examples of senders and whether they are attack or genuine based on their "
            "motion and EEBL behaviour. After the examples, classify a new sender.\n\n"
            "Examples:\n"
            "{FEW_SHOT_EXAMPLES}\n\n"
            "Now classify the following log record:\n"
            "{LOG_TEXT}\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Answer:"
        ),
    },

    # 3) IMAIHighSpeed
    "IMAIHighSpeed": {
        "zero_shot": (
            "You are detecting ATTACK vs GENUINE behaviour in V2X logs for intersection movement assist (IMA).\n\n"
            "Attack type: IMAHighSpeed.\n"
            "In this attack, the sender may report unrealistically high or inconsistent speeds near an intersection, "
            "which could cause other vehicles to react incorrectly.\n\n"
            "Definitions:\n"
            "- \"attack\": the sender's reported speed and motion look unrealistic or unsafe for the context.\n"
            "- \"genuine\": the sender's speed and motion look plausible for a real vehicle.\n\n"
            "You will be given a condensed description of one sender's state (speeds, accelerations, warnings, etc.).\n"
            "Decide if it is ATTACK or GENUINE.\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Log:\n"
            "{LOG_TEXT}\n\n"
            "Answer:"
        ),
        "few_shot": (
            "You are detecting ATTACK vs GENUINE behaviour in intersection-related V2X logs (IMAHighSpeed).\n\n"
            "Below are labeled examples of messages that are either attack or genuine with respect to "
            "IMAHighSpeed behaviour. After the examples, classify a new message.\n\n"
            "Examples:\n"
            "{FEW_SHOT_EXAMPLES}\n\n"
            "Now classify the following log record:\n"
            "{LOG_TEXT}\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Answer:"
        ),
    },

    # 4) RandomPosition
    "RandomPosition": {
        "zero_shot": (
            "You are a classifier for a vehicle-to-everything (V2X) network.\n\n"
            "Attack type: RandomPosition.\n"
            "In this attack, the sender may report positions or motion that are clearly unrealistic or "
            "inconsistent with normal driving (e.g., sudden large jumps, impossible locations).\n\n"
            "Definitions:\n"
            "- \"attack\": the sender's reported position/motion is clearly unrealistic or inconsistent.\n"
            "- \"genuine\": the sender behaves like a normal vehicle with plausible position and motion.\n\n"
            "You will be given one log entry in natural language describing a sender and receiver.\n"
            "Decide if it is ATTACK or GENUINE.\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Log:\n"
            "{LOG_TEXT}\n\n"
            "Answer:"
        ),
        "few_shot": (
            "You are detecting RandomPosition misbehavior in V2X logs.\n\n"
            "Below are labeled examples of messages that are either attack or genuine. After the examples, "
            "classify a new message.\n\n"
            "Examples:\n"
            "{FEW_SHOT_EXAMPLES}\n\n"
            "Now classify the following log record:\n"
            "{LOG_TEXT}\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Answer:"
        ),
    },

    # 5) RandomSpeedOffset
    "RandomSpeedOffset": {
        "zero_shot": (
            "You are detecting ATTACK vs GENUINE behaviour in V2X logs.\n\n"
            "Attack type: RandomSpeedOffset.\n"
            "In this attack, the sender may report speeds that are randomly offset from realistic values "
            "for its motion (too high or too low relative to context and acceleration).\n\n"
            "Definitions:\n"
            "- \"attack\": the reported speed looks suspicious or inconsistent with the rest of the state.\n"
            "- \"genuine\": the reported speed and motion look plausible for normal driving.\n\n"
            "You will be given one log entry describing sender and receiver speeds, accelerations, and distances.\n"
            "Decide if it is ATTACK or GENUINE.\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Log:\n"
            "{LOG_TEXT}\n\n"
            "Answer:"
        ),
        "few_shot": (
            "You are detecting RandomSpeedOffset misbehavior in V2X logs.\n\n"
            "Below are labeled examples of messages that are either attack or genuine based on their speed behaviour. "
            "After the examples, classify a new message.\n\n"
            "Examples:\n"
            "{FEW_SHOT_EXAMPLES}\n\n"
            "Now classify the following log record:\n"
            "{LOG_TEXT}\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Answer:"
        ),
    },

    # 6) SuddenAppearance
    "SuddenAppearance": {
        "zero_shot": (
            "You are detecting SuddenAppearance misbehavior in V2X logs.\n\n"
            "In a SuddenAppearance attack, a sender appears near the receiver in an implausible way, as if it "
            "teleported into or near the scene without a normal approach.\n\n"
            "Definitions:\n"
            "- \"attack\": the log belongs to a SuddenAppearance attack (implausible appearance).\n"
            "- \"genuine\": the log belongs to normal behaviour (plausible motion into the scene).\n\n"
            "You will be given one log entry describing sender/receiver states and distances.\n"
            "Decide if it is ATTACK or GENUINE.\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Log:\n"
            "{LOG_TEXT}\n\n"
            "Answer:"
        ),
        "few_shot": (
            "You are detecting SuddenAppearance misbehavior in V2X logs.\n\n"
            "Below are labeled examples of logs where vehicles either enter the scene normally (genuine) "
            "or appear implausibly (attack). After the examples, classify a new log.\n\n"
            "Examples:\n"
            "{FEW_SHOT_EXAMPLES}\n\n"
            "Now classify the following log record:\n"
            "{LOG_TEXT}\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Answer:"
        ),
    },

    # 7) TargetedConstantPosition
    "TargetedConstantPosition": {
        "zero_shot": (
            "You are detecting TargetedConstantPosition misbehavior in V2X logs.\n\n"
            "In this attack, the sender may keep reporting a position that does not match realistic motion "
            "or the true situation (e.g., artificially fixed or nearly fixed position).\n\n"
            "Definitions:\n"
            "- \"attack\": the reported position appears unnaturally constant or inconsistent with context.\n"
            "- \"genuine\": the position and motion look realistic for a real vehicle.\n\n"
            "You will be given one log entry describing sender/receiver speeds and positions.\n"
            "Decide if it is ATTACK or GENUINE.\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Log:\n"
            "{LOG_TEXT}\n\n"
            "Answer:"
        ),
        "few_shot": (
            "You are detecting TargetedConstantPosition misbehavior in V2X logs.\n\n"
            "Below are labeled examples of messages that are either attack or genuine for this scenario. "
            "After the examples, classify a new message.\n\n"
            "Examples:\n"
            "{FEW_SHOT_EXAMPLES}\n\n"
            "Now classify the following log record:\n"
            "{LOG_TEXT}\n\n"
            "Return exactly one word: attack or genuine.\n\n"
            "Answer:"
        ),
    },
}

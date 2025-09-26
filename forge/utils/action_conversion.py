# forge/data/processing/action_conversion.py
# (This is the complete, correct code from the smoloperator context)
from forge.utils.function_parser import FunctionCall


def rename_parameters(action: FunctionCall):
    if not action.parameters:
        return
    new_params = {f"arg_{i}": v for i, v in enumerate(action.parameters.values())}
    action.parameters = new_params


def change_argument_name(action: FunctionCall):
    if "arg_0" in action.parameters:
        if isinstance(action.parameters["arg_0"], (list, tuple)):
            action.parameters["from_coord"] = tuple(
                float(c) for c in action.parameters["arg_0"]
            )
        else:
            action.parameters["x"] = float(action.parameters["arg_0"])
        del action.parameters["arg_0"]
    if "arg_1" in action.parameters:
        if isinstance(action.parameters["arg_1"], (list, tuple)):
            action.parameters["to_coord"] = tuple(
                float(c) for c in action.parameters["arg_1"]
            )
        else:
            action.parameters["y"] = float(action.parameters["arg_1"])
        del action.parameters["arg_1"]


def action_conversion(
    actions: list[FunctionCall], resolution: tuple[int, int]
) -> list[FunctionCall]:
    for i, action in enumerate(actions):
        rename_parameters(action)
        name = action.function_name
        if name == "mobile.home":
            action.function_name = "navigate_home"
        elif name == "mobile.open_app":
            action.function_name = "open_app"
        elif name == "mobile.swipe":
            action.function_name = "swipe"
            change_argument_name(action)
        elif name == "mobile.back":
            action.function_name = "navigate_back"
        elif name == "mobile.long_press":
            action.function_name = "long_press"
            change_argument_name(action)
        elif name in ["mobile.terminate", "answer"]:
            action.function_name = "final_answer"
        elif name == "mobile.wait":
            action.function_name = "wait"
            if "arg_0" in action.parameters:
                action.parameters["seconds"] = int(action.parameters.pop("arg_0"))
        elif name == "pyautogui.click":
            action.function_name = "click"
            change_argument_name(action)
        elif name == "pyautogui.doubleClick":
            action.function_name = "double_click"
            change_argument_name(action)
        elif name == "pyautogui.rightClick":
            action.function_name = "right_click"
            change_argument_name(action)
        elif name in ["pyautogui.hotkey", "pyautogui.press"]:
            action.function_name = "press"
            if "arg_0" in action.parameters:
                action.parameters["keys"] = action.parameters.pop("arg_0")
        elif name == "pyautogui.moveTo":
            action.function_name = "move_mouse"
            change_argument_name(action)
        elif name == "pyautogui.write":
            action.function_name = "type"
            if "arg_0" in action.parameters:
                action.parameters["text"] = action.parameters.pop("arg_0")
        elif name in ["pyautogui.scroll", "pyautogui.hscroll"]:
            val = action.parameters.pop("arg_0")
            action.function_name = "scroll"
            action.parameters["amount"] = int(abs(val * 100))
            if name == "pyautogui.hscroll":
                action.parameters["direction"] = "left" if val < 0 else "right"
            else:
                action.parameters["direction"] = "up" if val < 0 else "down"
        elif name == "pyautogui.dragTo":
            action.function_name = "drag"
            change_argument_name(action)
        action.original_string = action.to_string()
    return actions

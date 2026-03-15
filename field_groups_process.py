import logging
import asyncio


def random_message(typ: str) -> str:
    import random
    messages = [
        ("Already in field group", "adds"),
        ("Added", "adds"),
        ("Invalid Bloomberg field", None),
        ("Deleted", "deletes"),
        ("Not in field group", "deletes"),
    ]
    filtered_messages = [msg for msg in messages if msg[1] == typ or msg[1] is None]
    return random.choice(filtered_messages)[0] if filtered_messages else ""


async def process_field_group(
    inp_data: dict[str, str|bool|list[str]]
) -> dict[str, list[dict[str, str]]]:
    logging.info("Processing field groups...")
    await asyncio.sleep(2)
    ret_dict = {}
    
    adds = []
    for add_field in inp_data.get("adds", []):
        adds.append({
            "field": add_field,
            "message": random_message("adds")
        })
    ret_dict["adds"] = adds

    deletes = []
    for del_field in inp_data.get("deletes", []):
        deletes.append({
            "field": del_field,
            "message": random_message("deletes")
        })
    ret_dict["deletes"] = deletes
    
    logging.info("Done processing field groups.")
    return ret_dict

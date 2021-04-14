# Function to make websocket response generic
def getWebsocketResponseDict(type_name, content, is_success, is_authenticated):
    if is_success:
        return {
            "auth_status": "authenticated" if is_authenticated else "unauthenticated",
            "is_success": True,
            "data": content,
            "type": type_name,
        }
    else:
        return {
            "auth_status": "authenticated" if is_authenticated else "unauthenticated",
            "is_success": False,
            "data": {"error": content},
            "type": type_name,
        }


def getFactoryChannelGroupName(factory_id):
    return f"factory_{factory_id}"
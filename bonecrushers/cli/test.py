from bonecrushers.library.position import Positioner

def main():

    try:
        p = Positioner()
        print(f"The test was successful.")
    except RuntimeError as ex:
        print(f"The test was not successful: {ex}")

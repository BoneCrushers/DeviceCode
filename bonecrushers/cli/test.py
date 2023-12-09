from bonecrushers.library.position import Positioner

def main():

    try:
        p = Positioner()
        print(f"The test was successful.")
        print(p.temp_c)

        import timeit
        print(timeit.timeit("p.temp_c",number=50,globals={"p":p}))
    except RuntimeError as ex:
        print(f"The test was not successful: {ex}")

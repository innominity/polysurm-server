import numpy as np
from typing import Callable

def eval_rozenbrock(target_column: str, config_dict: dict):
    results = {}
    #cache_file = pathlib.Path(__file__).parent.joinpath('cache.json')
    #cache = json_load(cache_file)

    for i in config_dict:
        config = config_dict[i]

        # hash_str = get_hash(config | {'case_id': case_id})
        result: dict = {} #cache.get(hash_str, {})

        if not result:
            func = make_software(rozenbrock)
            output = func(config)

            if output is None:
                continue

            result[target_column] = output
            #cache[hash_str] = result

        results[i] = result

    # json_save(cache, cache_file)
    return results

def ackley(
    x: np.ndarray,
    a: float = 20,
    b: float = 0.2,
    c: float = 2 * np.pi,
):
    return (
        -a * np.exp(-b * np.sqrt(np.mean(x**2, axis=-1)))
        - np.exp(np.mean(np.cos(c * x), axis=-1))
        + a
        + np.e
    )


def rozenbrock(
    x: np.ndarray,
    a: float = 1,
    b: float = 100,
):
    print(x)
    print(a)
    print(b)
    return np.sum(
        b * (x[..., 1:] - x[..., :-1] ** 2) ** 2 + (x[..., :-1] - a) ** 2,
        axis=-1,
    )


def ackley2(
    x: np.ndarray,
    a: float = 20,
    b: float = 0.2,
    c: float = 2 * np.pi,
):
    return (
        -a * np.exp(-b * np.sqrt(np.mean(np.power(x, 2), axis=-1)))
        - np.exp(np.mean(np.cos(c * x), axis=-1))
        + a
        + np.e
    )


def rozenbrock2(
    x: np.ndarray,
    a: float = 1,
    b: float = 100,
):
    return np.sum(
        b * np.power(x[..., 1:] - np.power(x[..., :-1], 2), 2)
        + np.power(x[..., :-1] - a, 2),
        axis=-1,
    )


def make_software(
    f: Callable[[np.ndarray], float]
):
    def software(x: dict[str, float]) -> float:
        return f(np.array(list(x.values())))

    return software
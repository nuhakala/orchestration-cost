"""
Single entry-point to the tests. Goal is to unify the interface of running every
test and provide more user-friendly CLI-experience.

Does not do anything else than parse command line params and call the run
functions defined in individual test files under ./tests/
"""
import argparse
import importlib

MODULE_MAP = {
    ("cont", "k0s"): "tests.container_k0s",
    ("cont", "k3s"): "tests.container_k3s",
    ("cont", "kube"): "tests.container_kubeedge",

    ("knative", "k0s"): "tests.knative_k0s",
    ("knative", "k3s"): "tests.knative_k3s",
    ("knative", "kube"): "tests.knative_kubeedge",

    ("spinnat", "k0s"): "tests.spin_k0s_native",
    ("spinnat", "k3s"): "tests.spin_k3s_native",
    ("spincon", "k0s"): "tests.spin_k0s_container",
    ("spincon", "k3s"): "tests.spin_k3s_container",
    ("spincon", "kube"): "tests.spin_kubeedge",

    ("wc", "k0s"): "tests.wc_k0s",
    ("wc", "k3s"): "tests.wc_k3s",
    ("wc", "kube"): "tests.wc_kubeedge",
}


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "orchestrator",
        choices=["wc", "spinnat", "spincon", "cont", "knative"],
        help="Choose orchestrator",
    )

    parser.add_argument(
        "platform",
        choices=["k0s", "k3s", "kube"],
        help="Choose platform",
    )

    parser.add_argument(
        "scenario",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Choose Scenario",
    )

    parser.add_argument(
        "--parse",
        action="store_true",
        help="Parse data",
    )

    parser.add_argument(
        "--multi",
        action="store_true",
        help="Multi-node test",
    )

    parser.add_argument(
        "--dir",
        help="Dir extension to store test data",
    )

    args = parser.parse_args()

    module_name = MODULE_MAP[(args.orchestrator, args.platform)]

    module = importlib.import_module(module_name)

    dir = ""
    if args.dir != None:
        dir = f"-{args.dir}"
    module.run(
        scenario=args.scenario,
        parse=args.parse,
        multi=args.multi,
        dir=dir,
    )


if __name__ == "__main__":
    main()

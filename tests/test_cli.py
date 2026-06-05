from pathlib import Path

from curvinspect.cli import build_parser


def test_analyze_command_parser():
    parser = build_parser()

    args = parser.parse_args(
        [
            "analyze",
            "input.png",
            "--output",
            "output",
            "--method",
            "threshold",
            "--num-samples",
            "128",
        ]
    )

    assert args.command == "analyze"
    assert args.image == Path("input.png")
    assert args.output == Path("output")
    assert args.method == "threshold"
    assert args.num_samples == 128


def test_demo_command_parser():
    parser = build_parser()

    args = parser.parse_args(
        [
            "demo",
            "--image-output",
            "examples/input",
            "--output",
            "examples/output/demo",
            "--threshold",
            "1.5",
        ]
    )

    assert args.command == "demo"
    assert args.image_output == Path("examples/input")
    assert args.output == Path("examples/output/demo")
    assert args.threshold == 1.5
#!/usr/bin/env python
"""Build ``paper/results.json`` — the frozen record of every number the paper quotes.

The figures are files; the numbers read off them are not. They get copied into the
main text, the figure captions, ``paper/model-inventory.md`` and the SI, and each
copy can go stale on its own. Tidying this repository turned up exactly that: the
"What the re-run changed" section of ``model-inventory.md`` was labelled ``rerun_v3``
while every value in it was still ``rerun_v2``'s.

So each number is computed once, in ``src/workflow/results.py``, and frozen here.
``results.json`` is committed and is the gold standard::

    uv run python paper/build_results.py            # recompute and rewrite
    uv run python paper/build_results.py --check    # recompute and diff, write nothing

``--check`` is what ``tests/test_results_regression.py`` runs, and what `make test`
runs when the sweep is present. After a re-run it names the key that moved and by how
much, instead of leaving the drift to be spotted by eye.

Two tiers live in the file:

* **Always checkable** — ``landscape``, ``parameters`` and ``c14`` come from inputs
  that are versioned with this repository (the rasters, the Hydra config, the SI-2
  workbook), so any clone, and CI, can verify them.
* **Needs the sweep** — ``figure2``–``figure5`` come from
  ``out/south_china_evolution/rerun_v3``, which is gitignored (135 MB). Without it
  the check skips that tier rather than failing; fetch it with ``make fetch-rerun``.

Run from the repository root.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

# The landscape counts and the composed config already have exactly one producer —
# the script that builds the table workbook. Import it rather than recompute, so a
# cell count can never disagree between Table 1 and results.json.
from build_tables import landscape_counts, load_config  # noqa: E402

from src.workflow import c14  # noqa: E402
from src.workflow import figures as F  # noqa: E402
from src.workflow import results as R  # noqa: E402

OUT = ROOT / "paper" / "results.json"

#: The sweep the published figures were built from. Locked to ``rerun_v3`` on purpose:
#: the superseded batches are still on disk, and pointing at one would recompute
#: happily and quietly return numbers belonging to the pre-conversion runs.
SWEEP = ROOT / "out" / "south_china_evolution" / "rerun_v3"

#: SI-2, shipped with the submission; the source for Figure 1.
DATASET = ROOT / "data" / "si2_c14_sites.xlsx"

#: Significant figures kept in the file. Six is far tighter than any change worth
#: noticing and far looser than the last-bit noise a NumPy upgrade can introduce.
DIGITS = 6


def repo_tier() -> dict:
    """The numbers derivable from inputs this repository versions."""
    cfg = load_config()
    land = landscape_counts()
    dates = c14.load_c14_dates(DATASET)
    sites = c14.aggregate_sites(dates)
    coverage = c14.subsistence_coverage(dates, bin_width=50)
    older, younger = c14.overlap_window(coverage)

    return {
        "landscape": land,
        "parameters": {
            # Only the parameters a headline number is derived from. The full list is
            # Table S4, built from the same composed config by build_tables.py.
            "lim_h_per_cell": float(cfg.env.lim_h),
            "regional_forager_ceiling": int(cfg.env.lim_h * land["cells"]),
            "lam_farmer": float(cfg.env.lam_farmer),
            "lam_ricefarmer": float(cfg.env.lam_ricefarmer),
            "steps": int(cfg.time.end),
            "repeats": int(cfg.exp.repeats),
            "seed": int(cfg.seed),
        },
        "c14": {
            "n_dates": int(len(dates)),
            "n_sites": int(sites.shape[0]),
            "n_provinces": int(dates["province"].nunique()),
            "sites_by_subsistence": {
                str(k): int(v)
                for k, v in sites["subsistence"].value_counts().sort_index().items()
            },
            "oldest_cal_bp": float(dates["cal_from"].max()),
            "youngest_cal_bp": float(dates["cal_to"].min()),
            "coexistence_window_cal_bp": [float(older), float(younger)],
            "coexistence_fraction": float(c14.coexistence_fraction(dates, coverage)),
        },
    }


def _rel(path: Path) -> str:
    """Repository-relative when it can be, absolute otherwise — never a machine path
    in the committed file for the default sweep, and never a crash for an odd one."""
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def round_tree_tier(tier: dict) -> dict:
    """Round one tier to the file's precision.

    The regression test recomputes a tier on its own and compares it against the
    committed file, so it has to round with exactly the same rule the file was
    written with — hence one function rather than a second literal ``6``.
    """
    return R.round_tree(tier, DIGITS)


def build(sweep: Path = SWEEP) -> dict:
    """The whole file: the repo tier, plus the sweep tier when the sweep is on disk."""
    payload = {
        "_meta": {
            "built_by": "paper/build_results.py",
            "sweep": _rel(sweep),
            "tail_steps": F.TAIL_STEPS,
            "significant_digits": DIGITS,
        },
        **repo_tier(),
    }
    if sweep.exists():
        payload.update(R.compute_results(sweep))
    return round_tree_tier(payload)


def flatten(node, prefix: str = "") -> dict[str, object]:
    """``{"figure4.spread_ratio.lim_h": 1.397, ...}`` — one leaf per line, for diffing."""
    if isinstance(node, dict):
        out: dict[str, object] = {}
        for k, v in node.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
        return out
    return {prefix: node}


def diff(old: dict, new: dict) -> list[str]:
    """Human-readable leaf-by-leaf differences, oldest key order first."""
    a, b = flatten(old), flatten(new)
    lines = []
    for key in sorted(set(a) | set(b)):
        if key not in a:
            lines.append(f"  + {key} = {b[key]!r}  (new)")
        elif key not in b:
            lines.append(f"  - {key} = {a[key]!r}  (gone)")
        elif a[key] != b[key]:
            extra = ""
            if isinstance(a[key], (int, float)) and isinstance(b[key], (int, float)):
                if a[key]:
                    extra = f"   [{(b[key] - a[key]) / abs(a[key]):+.2%}]"
            lines.append(f"  ~ {key}: {a[key]!r} -> {b[key]!r}{extra}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="recompute and diff against the committed results.json; write nothing",
    )
    parser.add_argument(
        "--sweep",
        type=Path,
        default=SWEEP,
        help=f"sweep root to recompute from (default: {SWEEP.relative_to(ROOT)})",
    )
    args = parser.parse_args(argv)

    fresh = build(args.sweep)
    if not args.sweep.exists():
        print(
            f"note: {args.sweep} is absent, so figure2-5 are not recomputed.\n"
            "      fetch it with: make fetch-rerun",
            file=sys.stderr,
        )

    if args.check:
        if not OUT.exists():
            print(f"{OUT} does not exist yet; run without --check.", file=sys.stderr)
            return 1
        stored = json.loads(OUT.read_text(encoding="utf-8"))
        # A tier that could not be recomputed must not read as "deleted".
        stored = {k: v for k, v in stored.items() if k in fresh}
        changes = diff(stored, fresh)
        if changes:
            print(f"{OUT.name} is out of date ({len(changes)} change(s)):")
            print("\n".join(changes))
            print(
                "\nIf the re-run was intended, rebuild the file and update every place"
                "\nthat quotes these numbers (paper/model-inventory.md, the vault"
                "\nscenes, the figure notebooks):"
                "\n  uv run python paper/build_results.py"
            )
            return 1
        print(f"{OUT.name} is up to date ({len(flatten(fresh))} values).")
        return 0

    OUT.write_text(
        json.dumps(fresh, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)} ({len(flatten(fresh))} values)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

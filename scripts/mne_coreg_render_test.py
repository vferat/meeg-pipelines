#!/usr/bin/env python3
"""Generate a headless MNE coregistration image and save it to /data.

This is intended for headless container environments such as Docker/Apptainer.
It sets the PyVista off-screen backend, fetches or uses fsaverage, renders a
simple coregistration scene, and saves both a PNG image and a small HTML report.
"""
# /usr/local/bin/entrypoint.sh python /data/mne_coreg_render_test.py 
# /usr/local/bin/entrypoint.sh glxinfo -B
from __future__ import annotations

import os
from pathlib import Path


OUTPUT_DIR = Path("/data")
PNG_PATH = OUTPUT_DIR / "mne_coreg.png"
HTML_PATH = OUTPUT_DIR / "mne_coreg_report.html"


def create_mne_report() -> None:
    """Create an MNE Report and save it as HTML."""
    import mne

    data_path = Path(mne.datasets.sample.data_path(verbose=False))
    sample_dir = data_path / "MEG" / "sample"
    subjects_dir = data_path / "subjects"

    trans_path = sample_dir / "sample_audvis_raw-trans.fif"
    raw_path = sample_dir / "sample_audvis_filt-0-40_raw.fif"


    report = mne.Report(title="Coregistration check", verbose=False)
    report.add_bem(
        subject="sample",
        subjects_dir=subjects_dir,
        title="MRI & BEM",
        decim=40,
        width=256,
    )
    report.add_trans(
        trans=trans_path,
        info=raw_path,
        subject="sample",
        subjects_dir=subjects_dir,
        alpha=1.0,
        title="Coregistration",
    )
    report.save("/data/report_coregistration.html", overwrite=True, open_browser=False)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    create_mne_report()


if __name__ == "__main__":
    main()

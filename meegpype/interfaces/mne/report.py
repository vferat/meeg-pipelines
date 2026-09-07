import os
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    TraitedSpec,
    isdefined,
    Directory,
    File,
)
import mne


class MakeReportInputSpec(BaseInterfaceInputSpec):
    fname = traits.File(
        desc="Output file name. Use a name <dir>/<name>-trans.fif.", mandatory=True
    )
    subject = traits.Str(desc="Subject name (required)", mandatory=True)
    subjects_dir = Directory(desc="Subjects directory", exists=True, mandatory=True)
    info = traits.File(
        desc="Path to a file with measurement information.", exists=True, mandatory=True
    )
    raws = traits.List(traits.File(exist=True), desc="List of raw files")
    head_positions = traits.List(traits.File(exist=True), desc="List of head position figures")
    trans = traits.File(
        desc="The path to the head<->MRI transform *-trans.fif file produced during coregistration.",
        exists=True,
        mandatory=False,
    )
    forward = traits.File(
        desc="The path to the file containing forward solution.",
        exists=True,
        mandatory=False,
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=None,
    )


class MakeReportOutputSpec(TraitedSpec):
    html_report = File(desc="The report file in HTML format.", exists=True)
    hdf5_report = File(desc="The report file in hdf5 format.", exists=True)


class MakeReport(BaseInterface):
    input_spec = MakeReportInputSpec
    output_spec = MakeReportOutputSpec

    def _run_interface(self, runtime):
        import matplotlib.pyplot as plt

        inputs = {
            "raws": None,
            "head_positions": None,
            "trans": None,
            "forward": None,
            "overwrite": False,
            "verbose": None,
        }
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        fname = inputs["fname"]
        subject = inputs["subject"]
        subjects_dir = inputs["subjects_dir"]
        raws = inputs["raws"]
        info = inputs["info"]
        head_positions = inputs["head_positions"]
        trans = inputs["trans"]
        forward = inputs["forward"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        try:
            import pyvista as pv
            pv.OFF_SCREEN = True
        except (ImportError, OSError):
            raise RuntimeError(
                "PyVista is required for report generation.")

        # Create report
        report = mne.Report(
            info_fname=info,
            subjects_dir=subjects_dir,
            subject=subject,
            title=subject,
            cov_fname=None,
            baseline=None,
            image_format="auto",
            verbose=verbose,
        )
        if raws:
            for r, raw in enumerate(raws):
                title = os.path.basename(raw)
                report.add_raw(raw, title=title)
                if head_positions:
                    headposition = head_positions[r]
                    hp = mne.chpi.read_head_pos(headposition)
                    raw_ = mne.io.read_raw(raw)
                    info = raw_.info
                    fig, axes = plt.subplots(3, 2)
                    mne.viz.plot_head_positions(
                        hp,
                        info=info,
                        destination=info["dev_head_t"],
                        axes=axes,
                    )
                    for axes_ in axes:
                        for annotation in raw_.annotations:
                            if "bad" in annotation["description"].lower():
                                for ax in axes_:
                                    ax.axvspan(
                                        annotation["onset"],
                                        annotation["onset"] + annotation["duration"],
                                        color="red",
                                        alpha=0.5,
                                    )

                    report.add_figure(fig, title=f"{title} - Head Position",
                                      caption="Head position")

        report.add_bem(subject=subject, subjects_dir=subjects_dir, title="bem")

        if trans:
            report.add_trans(
                trans=trans,
                info=info,
                title="trans",
                subject=subject,
                subjects_dir=subjects_dir,
            )
        if forward:
            report.add_forward(
                forward, plot=True, title="forward", subject=subject, subjects_dir=subjects_dir
            )

        # Add sys_info
        report.add_sys_info(title="System Information")

        # Save
        cwd = os.getcwd()
        basename = os.path.join(cwd, os.path.splitext(os.path.basename(fname))[0])
        html_fname = basename + ".html"
        hdf5_fname = basename + ".hdf5"
        report.save(
            html_fname,
            sort_content=True,
            open_browser=False,
            overwrite=overwrite,
            verbose=verbose,
        )
        report.save(
            hdf5_fname,
            sort_content=True,
            open_browser=False,
            overwrite=overwrite,
            verbose=verbose,
        )
        return runtime

    def _list_outputs(self):
        fname = self.inputs.fname
        cwd = os.getcwd()
        basename = os.path.join(cwd, os.path.splitext(os.path.basename(fname))[0])
        html_fname = basename + ".html"
        hdf5_fname = basename + ".hdf5"
        outputs = self.output_spec().get()
        outputs["html_report"] = html_fname
        outputs["hdf5_report"] = hdf5_fname
        return outputs

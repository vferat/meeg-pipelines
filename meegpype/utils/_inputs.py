import json
from bids.layout import parse_file_entities, BIDSLayout
import mne_bids


def _ensure_subjects(subjects, layout):
    available_subjects = layout.get_subjects()
    available_subjects.remove("emptyroom")

    valide_subjects = []
    if subjects is None:
        return available_subjects
    else:
        for subject in subjects:
            subject = subject.strip("sub-")
            if subject in available_subjects:
                valide_subjects.append(subject)
            else:
                raise ValueError(
                    f"Subject {subject} not found in BIDS dataset. Available subjects: {available_subjects}"
                )
    return valide_subjects

def _ensure_sessions(sessions, layout, subject):
    available_sessions = layout.get_sessions(subject=subject)
    valide_sessions = []
    if sessions is None:
        return available_sessions
    else:
        for session in sessions:
            session = session.strip("ses-")
            if session in available_sessions:
                valide_sessions.append(session)
            else:
                raise ValueError(
                    f"Session {session} not found in BIDS dataset for subject {subject}. Available sessions: {available_sessions}"
                )
    return valide_sessions


def _find_landmarks(t1ws, layout):
    for t1w in t1ws:
        json_entities = parse_file_entities(t1w)
        json_entities["extension"] = ".json"
        json_path = layout.build_path(json_entities)

        with open(json_path) as f:
            metadata = json.load(f)

        if "AnatomicalLandmarkCoordinates" in metadata:
            fiducials = metadata["AnatomicalLandmarkCoordinates"]
            return fiducials, t1w
    return None, None


def _find_meg(layout, subject, session, use_sidecar_only=False):
    meg_files = layout.get(subject=subject, session=session, datatype='meg', suffix='meg', extension=['fif', 'fif.gz'], return_type='file')
    raws = []
    emptyrooms = []
    crosstalks = []
    calibrations = []
    for meg_file in meg_files:
        entities = parse_file_entities(meg_file)
        if "task" in entities and entities["task"] == "noise":
            continue
        if "acquisition" in entities and entities["acquisition"] == "crosstalk":
            continue
        mne_bids_root = mne_bids.get_bids_path_from_fname(
                meg_file, check=True, verbose=None
            )
        raws.append(meg_file)
        # emptyrooms
        emptyroom_path = mne_bids_root.find_empty_room(
            use_sidecar_only=use_sidecar_only, verbose=None
        ).fpath
        emptyrooms.append(emptyroom_path)
        # crosstalks
        crosstalk_path = mne_bids_root.meg_crosstalk_fpath
        crosstalks.append(crosstalk_path)
        # calibration
        calibration_path = mne_bids_root.meg_calibration_fpath
        calibrations.append(calibration_path)

    return [raws, emptyrooms, crosstalks, calibrations]


def get_inputs(bids_root, subjects=None, sessions=None, use_sidecar_only=False):
    layout = BIDSLayout(bids_root, validate=False, derivatives=False)
    subjects = _ensure_subjects(subjects, layout)

    results = []
    for subject in subjects:
        configuration = {}
        configuration["subject"] = subject
        # Anat
        t1ws = layout.get(subject=subject, datatype='anat', suffix='T1w', extension=['nii', 'nii.gz'], return_type='file')
        if len(t1ws) == 0:
            raise ValueError(f"No T1w images found for subject {subject}.")

        # Find T1w fiducials
        fiducials, t1w_fiducials = _find_landmarks(t1ws, layout)

        t2ws = layout.get(subject=subject, datatype='anat', suffix='T2w', extension=['nii', 'nii.gz'], return_type='file')

        # MEG
        sessions = _ensure_sessions(sessions, layout, subject)
        for session in sessions:
            megs = _find_meg(layout, subject, session, use_sidecar_only)
            if len(megs) != 0:
                results.append([
                    subject,
                    session,
                    t1ws,
                    t2ws,
                    t1w_fiducials,
                    fiducials,
                    megs]
                )
    return results

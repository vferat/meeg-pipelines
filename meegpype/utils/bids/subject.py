
from bids.layout import parse_file_entities, BIDSLayout
import mne_bids

def get_anatomical_landmarks(t1ws, layout):
    # fiducials
    landmarks = None
    landmark_reference = None
    for t1w in t1ws:
        metatdata = layout.get_metadata(t1w)
        if "AnatomicalLandmarkCoordinates" in metatdata:
            landmarks = metatdata["AnatomicalLandmarkCoordinates"]
            landmark_reference = t1w
            break
    return landmarks, landmark_reference


def get_meg_recording_associated_files(meg_recording, use_sidecar_only):
    mne_bids_root = mne_bids.get_bids_path_from_fname(
            meg_recording, check=True, verbose=False
        )
    # emptyrooms
    emptyroom_path = mne_bids_root.find_empty_room(
        use_sidecar_only=use_sidecar_only, verbose=False
    )
    if emptyroom_path:
        emptyroom_path = emptyroom_path.fpath

    # crosstalks
    crosstalk_path = mne_bids_root.meg_crosstalk_fpath

    # calibration
    calibration_path = mne_bids_root.meg_calibration_fpath

    file_association = {
        "raw": meg_recording,
        "emptyroom": emptyroom_path,
        "crosstalk": crosstalk_path,
        "calibration": calibration_path,
    }
    return file_association


def get_session_recordings(layout, subject_id, session, use_sidecar_only):
    meg_recordings = layout.get(subject=subject_id, session=session, datatype='meg', suffix='meg', extension=['fif', 'fif.gz'], return_type='file')
    file_associations = []
    for meg_recording in meg_recordings:
        entities = parse_file_entities(meg_recording)
        if "task" in entities and entities["task"] == "noise":
            continue
        if "acquisition" in entities and entities["acquisition"] == "crosstalk":
            continue
        file_association = get_meg_recording_associated_files(meg_recording, use_sidecar_only=use_sidecar_only)
        file_associations.append(file_association)
    return file_associations


def get_meg_recordings_per_session(layout, subject_id, sessions, use_sidecar_only=False):
    if sessions is None:
        available_sessions = layout.get_sessions(subject=subject_id)
    else:
        available_sessions = layout.get_sessions(subject=subject_id, session=sessions)
    sessions_id = []
    sessions_raws = []
    sessions_emptyrooms = []
    sessions_crosstalks = []
    sessions_calibrations = []
    if len(available_sessions) == 0:  # BIDS layout without session
        session_recordings = get_session_recordings(layout, subject_id, None, use_sidecar_only=use_sidecar_only)
        if len(session_recordings):
            sessions_id.append("")
            sessions_raws.append([recording['raw'] for recording in session_recordings])
            sessions_emptyrooms.append([recording['emptyroom'] for recording in session_recordings])
            sessions_crosstalks.append([recording['crosstalk'] for recording in session_recordings])
            sessions_calibrations.append([recording['calibration'] for recording in session_recordings])
    else:
        for available_session in available_sessions:
            session_recordings = get_session_recordings(layout, subject_id, available_session, use_sidecar_only=use_sidecar_only)
            if len(session_recordings):
                session_id = "ses-" + available_session
                sessions_id.append(session_id)
                sessions_raws.append([recording['raw'] for recording in session_recordings])
                sessions_emptyrooms.append([recording['emptyroom'] for recording in session_recordings])
                sessions_crosstalks.append([recording['crosstalk'] for recording in session_recordings])
                sessions_calibrations.append([recording['calibration'] for recording in session_recordings])
    return sessions_id, sessions_raws, sessions_emptyrooms, sessions_crosstalks, sessions_calibrations


def collect_subject_data(bids_dir, subject_id, sessions=None, validate=False, use_sidecar_only=False):
    layout = BIDSLayout(str(bids_dir), validate=validate)

    # Anat
    t1ws = layout.get(subject=subject_id, datatype='anat', suffix='T1w', extension=['nii', 'nii.gz'], return_type='file')
    t2ws = layout.get(subject=subject_id, datatype='anat', suffix='T2w', extension=['nii', 'nii.gz'], return_type='file')
    flairs = layout.get(subject=subject_id, datatype='anat', suffix='FLAIR', extension=['nii', 'nii.gz'], return_type='file')

    # Anatomical landmarks
    landmarks, landmark_reference = get_anatomical_landmarks(t1ws, layout)

    # MEG
    sessions_id, sessions_raws, sessions_emptyrooms, sessions_crosstalks, sessions_calibrations = get_meg_recordings_per_session(layout, subject_id, sessions, use_sidecar_only=use_sidecar_only)

    subject_data = {}
    subject_data["subject_id"] =  "sub-" + subject_id
    subject_data["t1ws"] = t1ws
    subject_data["t2ws"] = t2ws
    subject_data["flairs"] = flairs
    subject_data["landmarks"] = landmarks
    subject_data["landmarks_reference"] = landmark_reference
    subject_data["sessions_id"] = sessions_id
    subject_data["sessions_raws"] = sessions_raws
    subject_data["sessions_emptyrooms"] = sessions_emptyrooms
    subject_data["sessions_crosstalks"] = sessions_crosstalks
    subject_data["sessions_calibrations"] = sessions_calibrations
    return subject_data


import nibabel as nib
import pandas as pd

lh = nib.load(r"C:\Users\ferat\Documents\GitHub\meeg-pipelines\meegpype\data\fsLR\atlas_subparc374.L.32k_fs_LR.label.gii")

color_mapping_lh = {}
for label in lh.labeltable.labels:
    color_mapping_lh[label.key] = (label.red, label.green, label.blue, label.alpha)
color_mapping_lh

dict_lh = lh.labeltable.get_labels_as_dict()

data = []
for key in dict_lh.keys():
    label_name = dict_lh[key]
    label_value = key
    label_color = color_mapping_lh[key]
    d = {'label_name': label_name,
            'label_value': label_value,
            'R': int(label_color[0]*255),
            'G': int(label_color[1]*255),
            'B': int(label_color[2]*255),
            'A': int(label_color[3]*255)}
    data.append(d)
df_l = pd.DataFrame(data)

rh = nib.load(r"C:\Users\ferat\Documents\GitHub\meeg-pipelines\meegpype\data\fsLR\atlas_subparc374.R.32k_fs_LR.label.gii")
color_mapping_rh = {}
for label in rh.labeltable.labels:
    color_mapping_rh[label.key] = (label.red, label.green, label.blue, label.alpha)
color_mapping_rh

dict_rh = rh.labeltable.get_labels_as_dict()

data = []
for key in dict_rh.keys():
    label_name = dict_rh[key]
    label_value = key
    label_color = color_mapping_rh[key]
    d = {'label_name': label_name,
            'label_value': label_value,
            'R': int(label_color[0]*255),
            'G': int(label_color[1]*255),
            'B': int(label_color[2]*255),
            'A': int(label_color[3]*255)}
    data.append(d)
df_r = pd.DataFrame(data)

df_l['label_value'] += 1000
df_r['label_value'] += 2000

df = pd.concat([df_l, df_r], ignore_index=True)

# Export as FreeSurfer LUT format
def export_freesurfer_lut(df, output_path):
    """Export DataFrame to FreeSurfer ColorLUT format."""
    with open(output_path, 'w') as f:
        # Write header
        f.write("#$Id: CustomColorLUT.txt\n\n")
        f.write("#No. Label Name:                            R   G   B   A\n\n")
        
        # Write each label
        for _, row in df.iterrows():
            # Format: number, name (padded to ~40 chars), R, G, B, A
            label_num = int(row['label_value'])
            label_name = row['label_name']
            r, g, b, a = int(row['R']), int(row['G']), int(row['B']), int(row['A'])
            
            # Pad label name to align columns (similar to FreeSurfer format)
            f.write(f"{label_num:<4}{label_name:<40}{r:<4}{g:<4}{b:<4}{a}\n")
    
    print(f"LUT saved to: {output_path}")

# Export the LUT
output_lut_path = r"C:\Users\ferat\Documents\GitHub\meeg-pipelines\meegpype\data\fsLR\atlas_subparc374_ColorLUT.txt"
export_freesurfer_lut(df, output_lut_path)

df
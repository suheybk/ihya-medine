import csv, shutil, os
os.makedirs('icons', exist_ok=True)
for src,dst in list(csv.reader(open('rename_map.csv')))[1:]:
    if dst.strip():
        shutil.copy(f'icons_raw/{src}.png', f'icons/{dst.strip()}.png')
print('done -> icons/')

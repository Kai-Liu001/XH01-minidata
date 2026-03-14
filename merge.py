from pathlib import Path
import shutil

def merge_infrared_visible(source_dir: Path, infrared_dir: Path, visible_dir: Path):
    for folder in source_dir.iterdir():
        sub_folder = folder / "data/image"
        if not sub_folder.exists():
            continue
        
        for file in sub_folder.iterdir():
            # tiff extension
            if file.suffix == ".tiff":
                # move to infrared_dir
                shutil.move(file, infrared_dir / file.name)
            elif file.suffix == ".jpg":
                # move to visible_dir
                shutil.move(file, visible_dir / file.name)    
import shutil
from pathlib import Path
import subprocess
import fitz
import os

main_project_path= Path('C:\\Users\\azhar\\Desktop\\visualization')
target_dir = Path('C:\\Users\\azhar\\Desktop\\project_not_in_dataset')


def files(path) -> list[Path]:
    all_files = list(path.rglob('*.pdf')) + list(path.rglob('*.docx'))
    result = []
    for f in all_files:
        if "report" in f.name.lower():
            result.append(f)
    return result

def rename(root_dir: Path, prefix: str) -> None:
    for pdf in root_dir.rglob("*.pdf"):
        if "report" in pdf.name.lower():
            new_path = pdf.with_name(f"{prefix}_{pdf.name}")
            pdf.rename(new_path)
            print(f"Renamed: {pdf.name} → {new_path.name}")


def no_report_name(source_dir: Path) -> None:
    for pdf in source_dir.rglob("*.pdf"):
        if not "report" in pdf.name.lower():
            print(f"Found: {pdf.name}, {pdf.parent}\n")


def folder_name(pdf: Path) -> str:
    relative_path = pdf.relative_to(reports_path)
    return relative_path.parent


def is_macos_artifact(path: Path) -> bool:
    for part in path.parts:
        p = part.lower()
        if p.startswith("__macosx") or p.startswith("._") or p == ".ds_store" or p == "__MACOSX":
            return True
    return False


def move_files(source_dir: Path, target_dir: Path) -> None:
    for pdf in source_dir.rglob("*.pdf"):
        if is_macos_artifact(pdf):
            continue
        if "report" in pdf.name.lower():
            folder = folder_name(pdf)
            target_folder = target_dir / folder
            if target_folder.exists() and target_folder.is_dir():
                try:
                    shutil.move(str(pdf), str(target_folder / pdf.name))
                    print(f"Moved: {pdf.name} to {target_folder}")
                except Exception as e:
                    print(f"Error moving {pdf.name}: {e}")
            else:
                print(f"Skip: Target folder {target_folder} does not exist. Not moving.")

def convert_pdf_to_svg(source_dir: Path) -> None:
    for pdf in source_dir.rglob("*.pdf"):
        if is_macos_artifact(pdf):
            continue
        if "report" in pdf.name.lower():
            if "repaired" in pdf.name.lower():
                print(f"Пропущено: {pdf.name}")
                continue
            output_folder = pdf.parent / "svg_pages" 
            output_folder.mkdir(parents=True, exist_ok=True)
            
            inkscape_path = r"C:\Program Files\Inkscape\bin\inkscape.exe"
            
            try:
                doc = fitz.open(pdf)
                print(f"Обработка {pdf.name}: {len(doc)} стр.")
                
                for page_index in range(len(doc)):
                    page_num = page_index + 1
                    
                    temp_pdf = output_folder / f"temp_page_{page_num}.pdf"
                    new_doc = fitz.open() 
                    new_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)
                    new_doc.save(str(temp_pdf))
                    new_doc.close()
                    
                    svg_name = f"{pdf.stem}_page_{page_num}.svg"
                    svg_path = output_folder / svg_name
                    
                    subprocess.run([
                        inkscape_path,
                        str(temp_pdf),
                        "--export-type=svg",
                        f"--export-filename={str(svg_path)}"
                    ], check=True, capture_output=True)

                    with open(svg_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Ищем тег <image, который Inkscape использует для вставки растра
                        if '<image' not in content:
                            f.close() # Закрываем файл перед удалением
                            os.remove(svg_path)
                            print(f"Удалено: {svg_name} (изображений не найдено)")
                        else:
                            print(f"Сохранено: {svg_name} (содержит скриншоты)")
                    # 4. Удаляем временный PDF
                    os.remove(temp_pdf)
                    
                    print(f"Готово: Страница {page_num} -> {svg_name}")
                    
                doc.close()
                
            except Exception as e:
                print(f"Ошибка: {e}")

def main():
    convert_pdf_to_svg(main_project_path)

if __name__ == "__main__":
    main()
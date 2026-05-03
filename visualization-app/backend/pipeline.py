import sys
import io
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from utils import JsonYamlManager
from processors import DocumentProcessor, ImageExtractor
from metadata import MetadataExtractor, KeywordFilter, KeywordClassifier, MarkdownExtractor
from firebase import FirebasePushPDF, FirebaseClient, FirebasePushMD

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class Pipeline:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.doc_processor = DocumentProcessor()
        self.keyword_filter = KeywordFilter()
        self.firebase_client = FirebaseClient()
        self.firebase_pusher_md = FirebasePushMD()
        self.utils = JsonYamlManager()
        self.image_extractor = ImageExtractor()
        self._pdf_extractor = None
        self._md_extractor = None 
        self._classifier = None
    
    @property
    def pdf_extractor(self) -> MetadataExtractor:
        if self._pdf_extractor is None:
            self._pdf_extractor = MetadataExtractor()
        return self._pdf_extractor
    
    @property
    def md_extractor(self) -> MarkdownExtractor:
        if self._md_extractor is None:
            self._md_extractor = MarkdownExtractor()
        return self._md_extractor

    @property
    def classifier(self) -> KeywordClassifier:
        if self._classifier is None:
            self._classifier = KeywordClassifier()
        return self._classifier

    @property
    def files(self) -> list[Path]:
        return list(self.root_dir.rglob('report.md'))
    
    @property
    def svg_files(self) -> list[Path]:
        all_files = list(self.root_dir.rglob('*.svg'))
        return [f for f in all_files if f.is_file()]
    
    @property
    def images(self) -> list[Path]:
        paths = []
        for ext in ('*.png', '*.jpg', '*.jpeg'):
            paths += [p for p in self.root_dir.rglob(ext) if p.parent.name == 'images']
        return paths

    def run_upload(self) -> None:
        self.firebase_pusher_md.push_metadata(self.files)
        self.firebase_pusher_md.push_keywords(self.files)
        self.firebase_pusher_md.push_images(self.images)

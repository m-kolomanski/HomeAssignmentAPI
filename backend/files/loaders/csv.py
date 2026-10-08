from backend.files.loaders.base import FileLoader
import polars as pl


class CsvFileLoader(FileLoader):
    def load(self) -> pl.LazyFrame:
        return pl.scan_csv(self.upload_file.file)

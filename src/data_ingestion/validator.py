from pathlib import Path


class FileValidator:
    ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"]
    MAX_FILE_SIZE_MB = 50                              

    def validate_file(self, file_path: str) -> None:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. "
                f"Allowed types: {self.ALLOWED_EXTENSIONS}"
            )

        # add this block after the extension check
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"File size {size_mb:.1f}MB exceeds "
                f"limit of {self.MAX_FILE_SIZE_MB}MB"
            )
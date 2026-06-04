from pathlib import Path


class FileValidator:
    ALLOWED_EXTENSIONS = [".csv", ".xlsx"]

    def validate_file(self, file_path: str) -> None:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. "
                f"Allowed types: {self.ALLOWED_EXTENSIONS}"
            )
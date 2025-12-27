from pathlib import Path


class Settings:
    database_path: str = "agendalo.db"
    database_url: str = f"sqlite:///{database_path}"

    @classmethod
    def get_database_path(cls) -> str:
        return cls.database_path


settings = Settings()


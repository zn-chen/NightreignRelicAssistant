from __future__ import annotations

from pathlib import Path

from services.save_service import SaveService


def test_parse_vdf_extracts_users():
    content = '"users"\n{\n  "12345678901234567"\n  {\n    "AccountName" "test"\n    "PersonaName" "Tester"\n    "MostRecent" "1"\n  }\n}'

    data = SaveService._parse_vdf(content)

    assert data["users"]["12345678901234567"]["PersonaName"] == "Tester"


def test_backup_rename_and_delete(tmp_path: Path):
    service = SaveService(steam_path="", backup_dir=tmp_path / "backups")
    steam_id = "12345678901234567"
    save_dir = service.SAVE_DIR_BASE / steam_id
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / service.SAVE_FILENAME
    save_path.write_text("save-data", encoding="utf-8")

    success, _ = service.backup_save(steam_id, "slot1")
    assert success is True
    backups = service.get_backups(steam_id)
    assert len(backups) == 1

    success, _ = service.rename_backup(backups[0]["path"], "slot2")
    assert success is True
    backups = service.get_backups(steam_id)
    assert backups[0]["display_name"] == "slot2"

    success, _ = service.delete_backup(backups[0]["path"])
    assert success is True
    assert service.get_backups(steam_id) == []

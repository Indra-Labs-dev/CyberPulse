from __future__ import annotations

import re
from datetime import datetime

import yaml

from app.core.exceptions import NotFoundError
from app.models.enums import SignatureType
from app.models.signature import Signature
from app.repositories.signature_repo import SignatureRepository
from app.schemas.signature import (
    SigmaGenerateRequest,
    SignatureValidationResult,
    YaraGenerateRequest,
)

_HASH_PATTERNS = {
    32: "md5",
    40: "sha1",
    64: "sha256",
}

_VALID_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class SignatureService:
    def __init__(self, repo: SignatureRepository) -> None:
        self.repo = repo

    def generate_yara(self, data: YaraGenerateRequest) -> str:
        rule_name = re.sub(r"[^A-Za-z0-9_]", "_", data.name) or "generated_rule"
        if not _VALID_NAME.match(rule_name):
            rule_name = f"rule_{rule_name}"

        lines = [f"rule {rule_name}", "{"]
        lines.append("    meta:")
        if data.description:
            lines.append(f'        description = "{data.description}"')
        lines.append('        generated_by = "CyberPulse"')
        lines.append(f'        date = "{datetime.utcnow().date().isoformat()}"')

        string_defs = []
        if data.strings:
            lines.append("    strings:")
            for index, value in enumerate(data.strings):
                escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                var_name = f"$s{index}"
                lines.append(f'        {var_name} = "{escaped}" ascii wide')
                string_defs.append(var_name)

        condition_parts = []
        if string_defs:
            condition_parts.append("any of (" + ", ".join(string_defs) + ")")
        for digest in data.hashes:
            algo = _HASH_PATTERNS.get(len(digest.strip()))
            if algo:
                condition_parts.append(f'hash.{algo}(0, filesize) == "{digest.strip().lower()}"')

        lines.append("    condition:")
        lines.append("        " + (" or ".join(condition_parts) if condition_parts else "false"))
        lines.append("}")

        return "\n".join(lines)

    def generate_sigma(self, data: SigmaGenerateRequest) -> str:
        rule = {
            "title": data.name,
            "description": data.description or f"Règle générée par CyberPulse pour {data.name}",
            "status": "experimental",
            "logsource": data.log_source or {"category": "process_creation", "product": "windows"},
            "detection": {
                "selection": data.detection_selection or {"EventID": 1},
                "condition": "selection",
            },
            "level": data.level,
            "tags": ["cyberpulse.generated"],
        }
        return yaml.safe_dump(rule, sort_keys=False, allow_unicode=True)

    def validate(self, type_: SignatureType, rule_text: str) -> SignatureValidationResult:
        if type_ == SignatureType.YARA:
            return self._validate_yara(rule_text)
        return self._validate_sigma(rule_text)

    def _validate_yara(self, rule_text: str) -> SignatureValidationResult:
        errors = []
        if not re.search(r"\brule\s+[A-Za-z_][A-Za-z0-9_]*\s*\{", rule_text):
            errors.append("Déclaration 'rule <nom> {' manquante ou invalide.")
        if rule_text.count("{") != rule_text.count("}"):
            errors.append("Accolades non équilibrées.")
        if "condition:" not in rule_text:
            errors.append("Section 'condition:' manquante (obligatoire en YARA).")
        return SignatureValidationResult(is_valid=not errors, errors=errors)

    def _validate_sigma(self, rule_text: str) -> SignatureValidationResult:
        errors = []
        try:
            parsed = yaml.safe_load(rule_text)
        except yaml.YAMLError as exc:
            return SignatureValidationResult(is_valid=False, errors=[f"YAML invalide: {exc}"])

        if not isinstance(parsed, dict):
            return SignatureValidationResult(is_valid=False, errors=["Le document Sigma doit être un mapping YAML."])

        for required_field in ("title", "logsource", "detection"):
            if required_field not in parsed:
                errors.append(f"Champ obligatoire manquant: '{required_field}'.")

        detection = parsed.get("detection", {})
        if isinstance(detection, dict) and "condition" not in detection:
            errors.append("La section 'detection' doit contenir une 'condition'.")

        return SignatureValidationResult(is_valid=not errors, errors=errors)

    async def get(self, signature_id: int) -> Signature:
        signature = await self.repo.get_by_id(signature_id)
        if not signature:
            raise NotFoundError("Signature not found")
        return signature

    async def list(self, type_: SignatureType | None) -> list[Signature]:
        return await self.repo.list(type_)

    async def save(self, user_id: int, name: str, type_: SignatureType, rule_text: str, source_description: str | None) -> Signature:
        validation = self.validate(type_, rule_text)
        signature = Signature(
            name=name,
            type=type_,
            rule_text=rule_text,
            source_description=source_description,
            is_valid=validation.is_valid,
            created_by=user_id,
        )
        return await self.repo.create(signature)

    async def delete(self, signature_id: int) -> None:
        signature = await self.get(signature_id)
        await self.repo.delete(signature)

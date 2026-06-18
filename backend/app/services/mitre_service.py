from app.models.cve import CVE
from app.models.mitre import CveAttackMapping
from app.repositories.cve_repo import CVERepository
from app.repositories.mitre_repo import MitreRepository
from app.schemas.mitre import AttackMatrix, AttackMatrixEntry, AttackTechniqueOut, HeatmapEntry

SEED_TECHNIQUES = [
    {"technique_id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access",
     "description": "Exploitation d'une vulnérabilité dans une application exposée sur Internet."},
    {"technique_id": "T1133", "name": "External Remote Services", "tactic": "Initial Access",
     "description": "Utilisation de services d'accès distant externes (VPN, RDP)."},
    {"technique_id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution",
     "description": "Exécution de commandes via un interpréteur (shell, PowerShell, Python)."},
    {"technique_id": "T1203", "name": "Exploitation for Client Execution", "tactic": "Execution",
     "description": "Exploitation d'une vulnérabilité logicielle pour exécuter du code arbitraire."},
    {"technique_id": "T1547", "name": "Boot or Logon Autostart Execution", "tactic": "Persistence",
     "description": "Maintien de la persistance via des mécanismes de démarrage automatique."},
    {"technique_id": "T1068", "name": "Exploitation for Privilege Escalation", "tactic": "Privilege Escalation",
     "description": "Exploitation d'une vulnérabilité pour élever ses privilèges."},
    {"technique_id": "T1027", "name": "Obfuscated Files or Information", "tactic": "Defense Evasion",
     "description": "Obfuscation de fichiers ou de données pour échapper à la détection."},
    {"technique_id": "T1562", "name": "Impair Defenses", "tactic": "Defense Evasion",
     "description": "Désactivation ou altération des défenses de sécurité."},
    {"technique_id": "T1110", "name": "Brute Force", "tactic": "Credential Access",
     "description": "Tentatives répétées de découverte de identifiants valides."},
    {"technique_id": "T1003", "name": "OS Credential Dumping", "tactic": "Credential Access",
     "description": "Extraction d'identifiants depuis le système d'exploitation."},
    {"technique_id": "T1083", "name": "File and Directory Discovery", "tactic": "Discovery",
     "description": "Énumération de fichiers et répertoires sur le système compromis."},
    {"technique_id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery",
     "description": "Découverte de services réseau accessibles."},
    {"technique_id": "T1021", "name": "Remote Services", "tactic": "Lateral Movement",
     "description": "Utilisation de services distants légitimes pour se déplacer latéralement."},
    {"technique_id": "T1005", "name": "Data from Local System", "tactic": "Collection",
     "description": "Collecte de données depuis le système local compromis."},
    {"technique_id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration",
     "description": "Exfiltration de données via le canal de commande et contrôle."},
    {"technique_id": "T1486", "name": "Data Encrypted for Impact", "tactic": "Impact",
     "description": "Chiffrement de données pour empêcher l'accès (ransomware)."},
    {"technique_id": "T1498", "name": "Network Denial of Service", "tactic": "Impact",
     "description": "Saturation des ressources réseau pour rendre un service indisponible."},
    {"technique_id": "T1071", "name": "Application Layer Protocol", "tactic": "Command and Control",
     "description": "Utilisation de protocoles applicatifs standards pour le C2."},
]

_KEYWORD_TO_TECHNIQUE = {
    "remote code execution": "T1190",
    "rce": "T1190",
    "vpn": "T1133",
    "command injection": "T1059",
    "shell": "T1059",
    "client": "T1203",
    "privilege": "T1068",
    "escalation": "T1068",
    "obfuscat": "T1027",
    "bypass": "T1562",
    "brute force": "T1110",
    "credential": "T1003",
    "denial of service": "T1498",
    "dos": "T1498",
    "ransomware": "T1486",
    "encrypt": "T1486",
    "exfiltrat": "T1041",
    "lateral": "T1021",
}


class MitreService:
    def __init__(self, mitre_repo: MitreRepository, cve_repo: CVERepository) -> None:
        self.mitre_repo = mitre_repo
        self.cve_repo = cve_repo

    async def ensure_seeded(self) -> None:
        await self.mitre_repo.seed_techniques(SEED_TECHNIQUES)

    async def get_matrix(self) -> AttackMatrix:
        await self.ensure_seeded()
        techniques = await self.mitre_repo.list_techniques()
        counts = await self.mitre_repo.mapping_counts()

        tactics: dict[str, list[AttackMatrixEntry]] = {}
        for technique in techniques:
            tactics.setdefault(technique.tactic, []).append(
                AttackMatrixEntry(
                    technique=AttackTechniqueOut.model_validate(technique),
                    mapped_cve_count=counts.get(technique.id, 0),
                )
            )
        return AttackMatrix(tactics=tactics)

    async def get_heatmap(self) -> list[HeatmapEntry]:
        await self.ensure_seeded()
        techniques = await self.mitre_repo.list_techniques()
        counts = await self.mitre_repo.mapping_counts()
        entries = [
            HeatmapEntry(
                technique_id=t.technique_id, name=t.name, tactic=t.tactic, count=counts.get(t.id, 0)
            )
            for t in techniques
        ]
        return sorted(entries, key=lambda e: e.count, reverse=True)

    def _infer_technique_codes(self, cve: CVE) -> list[str]:
        text = f"{cve.title} {cve.description or ''}".lower()
        matched = {code for keyword, code in _KEYWORD_TO_TECHNIQUE.items() if keyword in text}
        return list(matched) or ["T1190"]

    async def auto_map_cve(self, cve_id: int) -> list[CveAttackMapping]:
        """Maps a CVE onto likely MITRE ATT&CK techniques.

        Uses keyword heuristics over the CVE description as a stand-in for the
        IA-based mapping described in the spec; swap `_infer_technique_codes`
        for a real model call once one is available.
        """
        await self.ensure_seeded()
        cve = await self.cve_repo.get_by_id(cve_id)
        if not cve:
            return []

        codes = self._infer_technique_codes(cve)
        created: list[CveAttackMapping] = []
        for code in codes:
            technique = await self.mitre_repo.get_technique_by_code(code)
            if not technique:
                continue
            if await self.mitre_repo.mapping_exists(cve_id, technique.id):
                continue
            mapping = await self.mitre_repo.create_mapping(
                CveAttackMapping(cve_id=cve_id, technique_id=technique.id, confidence=0.6)
            )
            created.append(mapping)
        return created

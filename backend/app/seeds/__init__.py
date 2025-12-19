"""
LSSP Seed Data Importer
시드 데이터를 데이터베이스에 로드
"""

import json
from decimal import Decimal
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.models.lssp import (
    LegalGround,
    DraftTemplate,
    DraftBlock,
)
from app.db.models.lssp.pipeline import KeypointRule

SEEDS_DIR = Path(__file__).parent
V2_10_PACK_DIR = Path(__file__).parents[3] / "docs/draft_upgrade/lssp_divorce_module_pack_v2_10/data"


def load_json(filename: str) -> dict:
    """Load JSON file from seeds directory"""
    with open(SEEDS_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_legal_grounds(db: Session) -> int:
    """Import legal_grounds.v2_01.json"""
    data = load_json("legal_grounds.v2_01.json")
    count = 0
    
    for ground in data.get("grounds", []):
        existing = db.query(LegalGround).filter_by(code=ground["code"]).first()
        if existing:
            continue
            
        db.add(LegalGround(
            code=ground["code"],
            name_ko=ground["name_ko"],
            elements=ground.get("elements", []),
            limitation=ground.get("limitation"),
            notes=ground.get("notes"),
            version=data.get("version", "v2.01"),
        ))
        count += 1
    
    db.commit()
    return count


def seed_draft_templates(db: Session) -> int:
    """Import draft_templates.v2_04.json"""
    data = load_json("draft_templates.v2_04.json")
    count = 0
    
    # Handle both list and dict structures
    if isinstance(data, list):
        templates = data
    else:
        templates = data.get("templates", [])
    
    for template in templates:
        existing = db.query(DraftTemplate).filter_by(id=template["id"]).first()
        if existing:
            continue
            
        db.add(DraftTemplate(
            id=template["id"],
            label=template["label"],
            schema=template.get("schema", {}),
            version=template.get("version", "v2.04"),
        ))
        count += 1
    
    db.commit()
    return count


def seed_draft_blocks(db: Session) -> int:
    """Import draft_blocks.v2_04.json"""
    data = load_json("draft_blocks.v2_04.json")
    count = 0
    
    # Handle both list and dict structures
    if isinstance(data, list):
        blocks = data
    else:
        blocks = data.get("blocks", [])
    
    for block in blocks:
        existing = db.query(DraftBlock).filter_by(id=block["id"]).first()
        if existing:
            continue
            
        db.add(DraftBlock(
            id=block["id"],
            label=block["label"],
            block_tag=block["block_tag"],
            template=block["template"],
            required_keypoint_types=block.get("required_keypoint_types", []),
            required_evidence_tags=block.get("required_evidence_tags", []),
            conditions=block.get("conditions"),
            legal_refs=block.get("legal_refs", []),
            version=block.get("version", "v2.04"),
        ))
        count += 1
    
    db.commit()
    return count


def seed_keypoint_rules(db: Session) -> int:
    """Import keypoint_rules.v2_10.json from v2.10 pack"""
    # Try v2.10 pack location first, then local seeds
    rules_file = V2_10_PACK_DIR / "keypoint_rules.v2_10.json"
    if not rules_file.exists():
        rules_file = SEEDS_DIR / "keypoint_rules.v2_10.json"

    if not rules_file.exists():
        # No rules file found, skip silently
        return 0

    with open(rules_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    version = data.get("version", "v2.10")

    for rule in data.get("rules", []):
        # Check if rule already exists (by evidence_type + kind + name)
        existing = db.query(KeypointRule).filter_by(
            evidence_type=rule["evidence_type"],
            kind=rule["kind"],
            name=rule["name"]
        ).first()

        if existing:
            continue

        db.add(KeypointRule(
            version=version,
            evidence_type=rule["evidence_type"],
            kind=rule["kind"],
            name=rule["name"],
            pattern=rule["pattern"],
            flags=rule.get("flags", ""),
            value_template=rule.get("value_template", {}),
            ground_tags=rule.get("ground_tags", []),
            base_confidence=Decimal(str(rule.get("base_confidence", 0.5))),
            base_materiality=rule.get("base_materiality", 40),
            is_enabled=True,
        ))
        count += 1

    db.commit()
    return count


def seed_all(db: Session) -> dict:
    """Run all seed imports"""
    results = {
        "legal_grounds": seed_legal_grounds(db),
        "draft_templates": seed_draft_templates(db),
        "draft_blocks": seed_draft_blocks(db),
        "keypoint_rules": seed_keypoint_rules(db),
    }
    return results


if __name__ == "__main__":
    # CLI usage
    from app.db.session import get_db_context
    
    with get_db_context() as db:
        results = seed_all(db)
        print("Seed import completed:")
        for name, count in results.items():
            print(f"  {name}: {count} records")

"""分子性质计算。用 rdkit 直接算，不引入 PyTDC（那个包很重且容易装崩）。"""

from __future__ import annotations

from typing import Any


def score_smiles(smiles_list: list[str]) -> list[dict[str, Any]]:
    """算 QED / 分子量 / LogP。rdkit 没装时只回 SMILES，不报错。"""
    try:
        from rdkit import Chem
        from rdkit.Chem import QED, Descriptors
    except ImportError:
        return [{"smiles": s} for s in smiles_list]

    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:  # 无效 SMILES，丢掉
            continue
        rows.append(
            {
                "smiles": smi,
                "qed": round(QED.qed(mol), 4),
                "mol_weight": round(Descriptors.MolWt(mol), 2),
                "logp": round(Descriptors.MolLogP(mol), 3),
                "num_atoms": mol.GetNumHeavyAtoms(),
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]], requested: int) -> dict[str, Any]:
    """生成类任务的通用统计。"""
    return {
        "molecules": rows,
        "requested": requested,
        "valid": len(rows),
        "unique": len({r["smiles"] for r in rows}),
        "validity": round(len(rows) / requested, 4) if requested else 0.0,
    }

"""
Importa contatos de eventos para dados/contatos_condominios.html (array const D).

A origem do evento vai no campo `origens` (ex.: "Sindexperience Stand"), que é
o mesmo filtro "Origem" da página. Se o telefone já existe na base, o contato
existente só recebe a origem nova — não duplica.

Uso:
    python dados/importar_contatos.py
Os arquivos ficam em dados/entradas/ e são declarados em FONTES.
"""
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
HTML = AQUI / "contatos_condominios.html"
ENTRADAS = AQUI / "entradas"
MARCA = "const D = "

# arquivo em dados/entradas  ->  (origem, referência)
FONTES = {
    "Sindexperience_2026_stand.xlsx": ("Sindexperience Stand", "stand Sindexperience 2026"),
}


def sem_acento(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()


def limpa(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def tel(t):
    d = re.sub(r"\D", "", limpa(t))
    if d.startswith("55") and len(d) in (12, 13):
        d = d[2:]
    d = d.lstrip("0")
    if len(d) == 11 and d[2] == "9":
        return d, "Válido - celular"
    if len(d) == 10 and d[2] in "2345":
        return d, "Válido - fixo"
    return d, ("Verificar" if d else "")


def registro(nome, cond, sindico, telefone, email, origem, ref):
    t, st = tel(telefone)
    nome_cond = limpa(cond)
    if re.fullmatch(r"[\s.\-–—_]*", nome_cond or "."):
        nome_cond = ""
    return {
        "id_condominio": "", "nome_condominio": nome_cond, "cep_numero": "",
        "nome_contato": limpa(nome).title() or "n/a",
        "tipo_contato": "Síndico" if sindico else "Outro", "outros_tipos": "",
        "cargo_original": "Síndico(a) profissional" if sindico else "Não é síndico(a) profissional",
        "telefone": t, "status_telefone": st, "telefone_2": "",
        "email": limpa(email).lower(), "data_nascimento": "", "origens": origem,
        "qtd_registros": "1", "referencias": ref, "flag": "",
        "tels": [{"t": t, "s": st}] if t else [],
    }


def carregar_novos():
    """Lê as planilhas de formulário do stand (colunas do Microsoft Forms)."""
    novos = []
    for arquivo, (origem, ref) in FONTES.items():
        caminho = ENTRADAS / arquivo
        if not caminho.exists():
            print(f"(ignorado, não encontrado) {arquivo}")
            continue
        df = pd.read_excel(caminho)
        df.columns = [str(c).strip() for c in df.columns]
        col = lambda parte: next(c for c in df.columns if parte in sem_acento(c))
        c_nome, c_tel = col("nome completo"), col("contato")
        c_mail, c_sind, c_cond = col("e-mail:"), col("sindico(a) profissional"), col("nome do condominio")
        for _, r in df.iterrows():
            if not limpa(r[c_nome]) and not limpa(r[c_tel]):
                continue
            novos.append(registro(r[c_nome], r[c_cond], sem_acento(r[c_sind]).startswith("sim"),
                                  r[c_tel], r[c_mail], origem, ref))
    return novos


def add_origem(r, origem):
    o = [x.strip() for x in r.get("origens", "").split(",") if x.strip()]
    if origem in o:
        return False
    r["origens"] = ", ".join(o + [origem])
    return True


def main():
    s = HTML.read_text(encoding="utf-8")
    i = s.index(MARCA) + len(MARCA)
    j = s.index("];", i) + 1
    D = json.loads(s[i:j])

    por_tel, por_nome = {}, {}
    for r in D:
        for t in r.get("tels", []):
            por_tel.setdefault(t["t"], r)
        if not r.get("tels"):
            por_nome.setdefault(sem_acento(r["nome_contato"]), r)

    novos = marcados = 0
    origens_vistas = set()
    for n in carregar_novos():
        origens_vistas.add(n["origens"])
        ex = por_tel.get(n["telefone"]) if n["telefone"] else por_nome.get(sem_acento(n["nome_contato"]))
        if ex:
            marcados += add_origem(ex, n["origens"])
            for k in ("email", "nome_condominio", "cargo_original"):
                if not ex.get(k) and n.get(k):
                    ex[k] = n[k]
            if ex["nome_contato"] == "n/a" and n["nome_contato"] != "n/a":
                ex["nome_contato"] = n["nome_contato"]
        else:
            D.append(n)
            novos += 1
            (por_tel if n["telefone"] else por_nome)[
                n["telefone"] or sem_acento(n["nome_contato"])] = n

    s = s[:i] + json.dumps(D, ensure_ascii=False) + s[j:]

    # garante que as origens novas apareçam no filtro da página
    ini = s.index("orgs = [")
    fim = s.index("]", ini) + 1
    lista = json.loads(s[ini + len("orgs = "):fim].replace("'", '"'))
    for o in sorted(origens_vistas):
        if o not in lista:
            lista.append(o)
    s = s[:ini] + "orgs = " + json.dumps(lista, ensure_ascii=False).replace('"', "'") + s[fim:]

    HTML.write_text(s, encoding="utf-8")
    print(f"{novos} contatos novos, {marcados} existentes receberam origem nova. Total: {len(D)}")


if __name__ == "__main__":
    main()

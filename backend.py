"""
Backend service for Document Dashboard & Delivery Overview Sync Engine.
Maintains PD207_Document_Plan_Filled_Status.xlsx preserving all formulas and formatting.
"""

import openpyxl
import os
import re
import io
import shutil
from datetime import datetime

# Default paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DOCUMENT_PLAN = os.path.join(BASE_DIR, "PD207_Document_Plan_Filled_Status.xlsx")

def get_default_delivery_overview():
    candidates = [
        os.path.join(BASE_DIR, "Copy of Copy of Copy of Delivery overview_Test2 - Copy.xlsx"),
        os.path.join(BASE_DIR, "Copy of Copy of Delivery overview_Test2 - Copy.xlsx"),
        os.path.join(BASE_DIR, "Copy of Copy of Delivery overview_Test2.xlsx")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join(BASE_DIR, "Copy of Copy of Delivery overview_Test2.xlsx")

DEFAULT_DELIVERY_OVERVIEW = get_default_delivery_overview()

PM_CODE_TO_NAME = {
    'SJ': 'Stefanie',
    'KH': 'Karan',
    'CM': 'Chettapong',
    'AA': 'Adisorn',
    'ML': 'Mladen'
}

COL_MAP = {
    'no': 1,             # A: Formula
    'project_no': 2,     # B: Value
    'project_name': 3,   # C: Value
    'pm': 4,             # D: Value
    'who': 5,            # E: Value
    'qg4': 6,            # F: Value
    'qg5': 7,            # G: Value
    'ifd': 8,            # H: Value
    'fat': 9,            # I: Value
    'pl': 10,            # J: Value
    'qg4_due': 11,       # K: Formula
    # QG4 Checklist
    'cert_list': 12,     # L
    'cert_mat_qg4': 13,  # M
    'fat_protocol': 14,  # N
    'cal_list': 15,      # O
    'adj_blank': 16,     # P
    'etk_draft': 17,     # Q
    'oem_draft': 18,     # R
    'manual_draft_qg4': 19, # S
    # IFD Checklist
    'ifd_due': 20,       # T: Formula
    'cal_cert': 21,      # U
    'cert_mat_ifd': 22,  # V: Formula or Value
    'adj_draft': 23,     # W
    'manual_draft_ifd': 24, # X
    # Final Checklist
    'final_due': 25,     # Y: Formula
    'etk_final': 26,     # Z: Formula or Value
    'oem_final': 27,     # AA: Formula or Value
    'cert_mat_final': 28,# AB: Formula or Value
    'adj_final': 29,     # AC
    'manual_final': 30,  # AD
    # Summary
    'docs_done': 31,     # AE: Formula
    'docs_req': 32,      # AF: Formula
    'progress': 33,      # AG: Formula
    'status': 34,        # AH: Formula
    'remark': 35         # AI
}

CHECKLIST_ITEMS = [
    ('cert_list', 'Cert. List', 'QG4', 'Certificate List'),
    ('cert_mat_qg4', 'Cert. Mat.', 'QG4', 'Material Certificate (QG4 Stage)'),
    ('fat_protocol', 'FAT protocol', 'QG4', 'FAT Test Protocol Procedure'),
    ('cal_list', 'Cal. list', 'QG4', 'Calibration Instrument List'),
    ('adj_blank', 'Adj. (Blank FORM)', 'QG4', 'Adjustment Blank Form'),
    ('etk_draft', 'ETK (BOM) draft', 'QG4', 'ETK (BOM) Spare Parts Draft'),
    ('oem_draft', 'OEM Draft', 'QG4', 'OEM Third-party Equipment Draft'),
    ('manual_draft_qg4', 'Manual draft', 'QG4', 'Machine Operation Manual Draft'),
    ('cal_cert', 'Cal. cert', 'IFD', 'Calibration Certificates'),
    ('cert_mat_ifd', 'Cert, Mat', 'IFD', 'Material Certificate (IFD Stage)'),
    ('adj_draft', 'Adj Draft', 'IFD', 'Machine Adjustment Draft'),
    ('manual_draft_ifd', 'Manual draft', 'IFD', 'Operating Manual (IFD Stage)'),
    ('etk_final', 'ETK', 'FINAL', 'Complete ETK Documentation'),
    ('oem_final', 'OEM', 'FINAL', 'Complete OEM Manuals'),
    ('cert_mat_final', 'Cert, Mat', 'FINAL', 'Final Material Certificates'),
    ('adj_final', 'Adj', 'FINAL', 'Final Adjustment Protocols'),
    ('manual_final', 'Manual', 'FINAL', 'Final Machine Operating Manual'),
]

CHECKLIST_KEYS = [k for k, _, _, _ in CHECKLIST_ITEMS]

def load_document_plan(filepath=DEFAULT_DOCUMENT_PLAN):
    """Loads all active projects from the Document Plan Excel sheet."""
    if not os.path.exists(filepath):
        return []

    wb_val = openpyxl.load_workbook(filepath, data_only=True)
    ws_val = wb_val['QG_Status']
    wb_form = openpyxl.load_workbook(filepath, data_only=False)
    ws_form = wb_form['QG_Status']

    projects = []
    for r in range(4, ws_val.max_row + 1):
        p_no = ws_val.cell(row=r, column=COL_MAP['project_no']).value
        p_name = ws_val.cell(row=r, column=COL_MAP['project_name']).value
        if p_no is None and p_name is None:
            continue

        p_no_str = str(p_no).strip() if p_no is not None else ""
        if not p_no_str:
            continue

        item = {'row_idx': r}
        for field, col in COL_MAP.items():
            val = ws_val.cell(row=r, column=col).value
            form = ws_form.cell(row=r, column=col).value
            item[field] = val
            item[f"{field}_formula"] = form if str(form).startswith('=') else None

        for k in CHECKLIST_KEYS:
            v = item.get(k)
            if v is not None:
                s = str(v).strip().upper()
                if s in ['1', '1.0']:
                    item[k] = 1
                elif s in ['0', '0.0']:
                    item[k] = 0
                elif 'N/A' in s:
                    item[k] = 'N/A'

        done, req, prog, status = calculate_metrics(item)
        item['calc_done'] = done
        item['calc_req'] = req
        item['calc_progress'] = prog
        item['calc_status'] = status

        # Map abbreviation to full PM name from Column F
        pm_val = item.get('pm')
        if pm_val:
            pm_str = str(pm_val).strip()
            item['pm'] = PM_CODE_TO_NAME.get(pm_str, pm_str)

        projects.append(item)

    return projects

def calculate_metrics(row_data):
    """Calculates Done, Required, Progress%, and Overall Status matching Excel formulas."""
    done = 0
    req = 0
    for key in CHECKLIST_KEYS:
        v = row_data.get(key)
        if v is None or v == '' or str(v).strip().upper() == 'N/A':
            continue
        v_str = str(v).strip()
        if v == 1 or v_str == '1' or v_str == '1.0':
            done += 1
            req += 1
        elif v == 0 or v_str == '0' or v_str == '0.0':
            req += 1
        else:
            try:
                float(v)
                req += 1
            except ValueError:
                pass

    prog = (done / req) if req > 0 else 0.0
    if req == 0:
        status = "Not Started"
    elif done == req:
        status = "Complete"
    elif done == 0:
        status = "Not Started"
    else:
        status = "In Progress"

    return done, req, prog, status

def parse_delivery_overview(overview_source):
    """Parses project headers and milestone calendar weeks (CW) from Delivery overview."""
    wb = openpyxl.load_workbook(overview_source, data_only=True)
    sheet_name = 'new machines' if 'new machines' in wb.sheetnames else wb.sheetnames[0]
    ws = wb[sheet_name]

    cw_headers = {}
    for c in range(15, ws.max_column + 1):
        v = ws.cell(row=8, column=c).value
        if v is not None:
            v_str = str(v).strip()
            if v_str.isdigit():
                cw_headers[c] = int(v_str)

    pm_map = {
        'stefanie': 'SJ',
        'karan': 'KH',
        'chettapong': 'CM',
        'adisorn': 'AA',
        'mladen': 'ML'
    }

    projects_raw = []
    current_proj = None

    for r in range(9, ws.max_row + 1):
        c3 = ws.cell(row=r, column=3).value
        c6 = ws.cell(row=r, column=6).value
        c7 = ws.cell(row=r, column=7).value
        c8 = ws.cell(row=r, column=8).value

        if c3 and re.search(r'5\d{4}', str(c3)) and not str(c3).strip().startswith(('../', 'file:')):
            first_line = str(c3).strip().splitlines()[0]
            m = re.search(r'(5\d{4})', first_line)
            if m:
                p_code = m.group(1)
                p_name = first_line.replace(p_code, '', 1).lstrip('_ -')
                if not p_name:
                    p_name = first_line

                pm_raw = str(c6).strip() if c6 else ''
                if not pm_raw:
                    for offset in range(1, 4):
                        c6_alt = ws.cell(row=r + offset, column=6).value
                        if c6_alt and not re.search(r'^\d+$', str(c6_alt).strip()):
                            pm_raw = str(c6_alt).strip()
                            break

                c8_str = str(c8).strip() if c8 else ''
                c7_str = str(c7).strip().lower() if c7 else ''

                if c8_str == 'QG status' or 'phase' in c7_str or 'delivery' in c7_str or 'hold' in c7_str:
                    if current_proj:
                        projects_raw.append(current_proj)
                    current_proj = {
                        'start_row': r,
                        'project_no': p_code,
                        'project_name': p_name,
                        'pm_full': pm_raw,
                        'pm_code': pm_map.get(pm_raw.lower(), pm_raw[:2].upper() if pm_raw else ''),
                        'rows': {}
                    }

        if current_proj:
            lbl = ws.cell(row=r, column=8).value or ws.cell(row=r, column=6).value or ''
            current_proj['rows'][r] = str(lbl).strip()

    if current_proj:
        projects_raw.append(current_proj)

    parsed_projects = []
    for p in projects_raw:
        start_r = p['start_row']
        qg_status_row = None
        q_quality_row = None
        delivery_row = None

        for r, lbl in p['rows'].items():
            if r >= start_r + 14:
                break
            if 'QG status' in lbl or r == start_r:
                if not qg_status_row:
                    qg_status_row = r
            if 'Q (quality)' in lbl:
                q_quality_row = r
            if 'D (Delivery)' in lbl:
                delivery_row = r

        def find_cw(terms, rows):
            for r in rows:
                if not r: continue
                for c, cw in cw_headers.items():
                    v = ws.cell(row=r, column=c).value
                    if v:
                        s = str(v).strip().upper()
                        for term in terms:
                            if term in s:
                                return f"CW{cw}"
            return ""

        def find_pl():
            for r in [delivery_row, qg_status_row]:
                if not r: continue
                candidates = []
                for c, cw in cw_headers.items():
                    v = ws.cell(row=r, column=c).value
                    if v:
                        s = str(v).strip().upper()
                        tokens = [t.strip() for t in s.split(',')]
                        if 'P' in tokens or 'L' in tokens or 'PL' in tokens or 'P,L' in s:
                            candidates.append(cw)
                if candidates:
                    return f"CW{candidates[-1]}"
            return ""

        qg4 = find_cw(['QG4'], [qg_status_row, q_quality_row])
        qg5 = find_cw(['QG5'], [qg_status_row, q_quality_row])
        ifd = find_cw(['IFD', 'IFS'], [qg_status_row, q_quality_row])
        fat = find_cw(['FAT'], [qg_status_row, q_quality_row])
        pl = find_pl()

        parsed_projects.append({
            'project_no': p['project_no'],
            'project_name': p['project_name'],
            'pm': p['pm_full'] or p['pm_code'],
            'pm_full': p['pm_full'],
            'pm_code': p['pm_code'],
            'qg4': qg4,
            'qg5': qg5,
            'ifd': ifd,
            'fat': fat,
            'pl': pl
        })

    return parsed_projects

def find_best_project_match(overview_proj, current_projects):
    o_no = str(overview_proj['project_no']).strip()
    o_name = str(overview_proj['project_name']).strip().lower()

    # 1. Exact match
    for p in current_projects:
        if str(p['project_no']).strip() == o_no:
            return p, 'exact'

    # 2. Similar 4-digit prefix
    for p in current_projects:
        c_no = str(p['project_no']).strip()
        if len(c_no) == 5 and len(o_no) == 5 and c_no[:4] == o_no[:4]:
            return p, 'prefix'

    # 3. Name match keywords
    for p in current_projects:
        c_name = str(p['project_name']).strip().lower()
        c_words = set(re.findall(r'\w{4,}', c_name))
        o_words = set(re.findall(r'\w{4,}', o_name))
        if c_words and o_words and (c_words & o_words):
            return p, 'name'

    return None, None

def sync_projects(current_projects, overview_projects, match_strategy='smart'):
    updated_list = [dict(p) for p in current_projects]
    sync_logs = []
    matched_curr_ids = set()

    max_row = max([p['row_idx'] for p in updated_list]) if updated_list else 3

    for o_p in overview_projects:
        matched_proj = None
        match_type = None

        if match_strategy == 'smart':
            unmatched = [p for p in updated_list if p['row_idx'] not in matched_curr_ids]
            matched_proj, match_type = find_best_project_match(o_p, unmatched)
        else:
            for p in updated_list:
                if str(p['project_no']).strip() == str(o_p['project_no']).strip():
                    matched_proj = p
                    match_type = 'exact'
                    break

        if matched_proj:
            matched_curr_ids.add(matched_proj['row_idx'])
            changes = []

            if match_type != 'exact':
                changes.append(f"Linked by {match_type} (Overview: {o_p['project_no']} -> Plan: {matched_proj['project_no']})")

            if o_p.get('pm') and matched_proj.get('pm') != o_p['pm']:
                changes.append(f"PM: {matched_proj.get('pm')} -> {o_p['pm']}")
                matched_proj['pm'] = o_p['pm']

            for field in ['qg4', 'qg5', 'ifd', 'fat', 'pl']:
                new_v = o_p.get(field)
                old_v = matched_proj.get(field)
                if new_v and new_v != old_v:
                    changes.append(f"{field.upper()}: {old_v or '-'} -> {new_v}")
                    matched_proj[field] = new_v

            done, req, prog, status = calculate_metrics(matched_proj)
            matched_proj['calc_done'] = done
            matched_proj['calc_req'] = req
            matched_proj['calc_progress'] = prog
            matched_proj['calc_status'] = status

            msg = f"Project {matched_proj['project_no']} ({matched_proj['project_name']}): " + (", ".join(changes) if changes else "Dates already up to date.")
            sync_logs.append({
                'project_no': matched_proj['project_no'],
                'overview_no': o_p['project_no'],
                'action': 'Updated' if changes else 'Matched',
                'details': msg
            })
        else:
            max_row += 1
            new_item = {
                'row_idx': max_row,
                'no': len(updated_list) + 1,
                'project_no': o_p['project_no'],
                'project_name': o_p['project_name'],
                'pm': o_p['pm'],
                'who': '',
                'qg4': o_p['qg4'],
                'qg5': o_p['qg5'],
                'ifd': o_p['ifd'],
                'fat': o_p['fat'],
                'pl': o_p['pl'],
                'qg4_due': o_p['qg4'],
                'ifd_due': o_p['ifd'],
                'final_due': o_p['pl'],
                'remark': 'Added from Delivery Overview'
            }
            # For new items, initialize empty or formula references
            for k in CHECKLIST_KEYS:
                new_item[k] = 'N/A'

            done, req, prog, status = calculate_metrics(new_item)
            new_item['calc_done'] = done
            new_item['calc_req'] = req
            new_item['calc_progress'] = prog
            new_item['calc_status'] = status

            updated_list.append(new_item)
            sync_logs.append({
                'project_no': o_p['project_no'],
                'overview_no': o_p['project_no'],
                'action': 'Added',
                'details': f"New project {o_p['project_no']} ({o_p['project_name']}) added to row {max_row}."
            })

    return updated_list, sync_logs

def populate_sheet_with_projects(ws, projects_data):
    """
    Populates Excel worksheet with projects_data while preserving and reinforcing
    all 602 formulas (LET, COUNTIF, COUNT, IF, IFERROR).
    """
    def safe_write_cell(cell, new_val, formula_val=None):
        if formula_val and str(formula_val).startswith('='):
            cell.value = formula_val
            return
        if str(cell.value).startswith('='):
            return
        cell.value = new_val

    for p in projects_data:
        r = p['row_idx']
        if r > 54:
            continue

        # Ensure Column A (No.) formula is always intact
        ws.cell(row=r, column=COL_MAP['no']).value = f'=IF(B{r}="","",ROW()-3)'

        # B, C, D (Project No, Name, PM)
        # Convert numeric string to int if digits
        p_no = p.get('project_no')
        if p_no is not None and str(p_no).isdigit():
            p_no = int(p_no)
        ws.cell(row=r, column=COL_MAP['project_no']).value = p_no
        ws.cell(row=r, column=COL_MAP['project_name']).value = p.get('project_name')
        ws.cell(row=r, column=COL_MAP['pm']).value = p.get('pm')

        # E (Who?)
        ws.cell(row=r, column=COL_MAP['who']).value = p.get('who')

        # F - J (QG4, QG5, IFD, FAT, PL)
        ws.cell(row=r, column=COL_MAP['qg4']).value = p.get('qg4')
        ws.cell(row=r, column=COL_MAP['qg5']).value = p.get('qg5')
        ws.cell(row=r, column=COL_MAP['ifd']).value = p.get('ifd')
        ws.cell(row=r, column=COL_MAP['fat']).value = p.get('fat')
        ws.cell(row=r, column=COL_MAP['pl']).value = p.get('pl')

        # K: QG4 Due formula
        ws.cell(row=r, column=COL_MAP['qg4_due']).value = (
            f'=IF($B{r}="","",_xlfn.LET(_xlpm.v,$F{r},_xlpm.n,'
            f'IF(ISNUMBER(_xlpm.v),_xlpm.v,'
            f'IF(LEFT(UPPER(TRIM(_xlpm.v)),2)="CW",IFERROR(VALUE(SUBSTITUTE(UPPER(TRIM(_xlpm.v)),"CW","")),""),"")),'
            f'IF(AND(ISNUMBER(_xlpm.n),_xlpm.n>=1,_xlpm.n<=52),"CW"&_xlpm.n,"")))'
        )

        # Checklists: QG4 (L-S)
        ws.cell(row=r, column=COL_MAP['cert_list']).value = p.get('cert_list')
        ws.cell(row=r, column=COL_MAP['cert_mat_qg4']).value = p.get('cert_mat_qg4')
        ws.cell(row=r, column=COL_MAP['fat_protocol']).value = p.get('fat_protocol')
        ws.cell(row=r, column=COL_MAP['cal_list']).value = p.get('cal_list')
        ws.cell(row=r, column=COL_MAP['adj_blank']).value = p.get('adj_blank')
        ws.cell(row=r, column=COL_MAP['etk_draft']).value = p.get('etk_draft')
        ws.cell(row=r, column=COL_MAP['oem_draft']).value = p.get('oem_draft')
        ws.cell(row=r, column=COL_MAP['manual_draft_qg4']).value = p.get('manual_draft_qg4')

        # T: IFD Due formula
        ws.cell(row=r, column=COL_MAP['ifd_due']).value = (
            f'=IF($B{r}="","",_xlfn.LET(_xlpm.v,$H{r},_xlpm.n,'
            f'IF(ISNUMBER(_xlpm.v),_xlpm.v,'
            f'IF(LEFT(UPPER(TRIM(_xlpm.v)),2)="CW",IFERROR(VALUE(SUBSTITUTE(UPPER(TRIM(_xlpm.v)),"CW","")),""),"")),'
            f'IF(AND(ISNUMBER(_xlpm.n),_xlpm.n>=1,_xlpm.n<=52),"CW"&_xlpm.n,"")))'
        )

        # Checklists: IFD (U-X)
        ws.cell(row=r, column=COL_MAP['cal_cert']).value = p.get('cal_cert')
        safe_write_cell(ws.cell(row=r, column=COL_MAP['cert_mat_ifd']), p.get('cert_mat_ifd'), f'=IF($B{r}="","",$M{r})')
        ws.cell(row=r, column=COL_MAP['adj_draft']).value = p.get('adj_draft')
        ws.cell(row=r, column=COL_MAP['manual_draft_ifd']).value = p.get('manual_draft_ifd')

        # Y: FINAL Due formula
        ws.cell(row=r, column=COL_MAP['final_due']).value = f'=IF(OR($B{r}="",$J{r}=""),"",$J{r})'

        # Checklists: FINAL (Z-AD)
        safe_write_cell(ws.cell(row=r, column=COL_MAP['etk_final']), p.get('etk_final'), f'=IF(OR($B{r}="",$Q{r}=""),"",$Q{r})')
        safe_write_cell(ws.cell(row=r, column=COL_MAP['oem_final']), p.get('oem_final'), f'=IF(OR($B{r}="",$R{r}=""),"",$R{r})')
        safe_write_cell(ws.cell(row=r, column=COL_MAP['cert_mat_final']), p.get('cert_mat_final'), f'=IF($B{r}="","",$M{r})')
        ws.cell(row=r, column=COL_MAP['adj_final']).value = p.get('adj_final')
        ws.cell(row=r, column=COL_MAP['manual_final']).value = p.get('manual_final')

        # AE - AH: Formulas
        ws.cell(row=r, column=COL_MAP['docs_done']).value = f'=COUNTIF($L{r}:$P{r},1)+COUNTIF($Q{r}:$S{r},1)+COUNTIF($U{r}:$X{r},1)+COUNTIF($Z{r}:$AD{r},1)'
        ws.cell(row=r, column=COL_MAP['docs_req']).value = f'=COUNT($L{r}:$P{r},$Q{r}:$S{r},$U{r}:$X{r},$Z{r}:$AD{r})'
        ws.cell(row=r, column=COL_MAP['progress']).value = f'=IF(AF{r}=0,0,AE{r}/AF{r})'
        ws.cell(row=r, column=COL_MAP['status']).value = f'=IF($B{r}="","",IF(AF{r}=0,"Not Started",IF(AE{r}=AF{r},"Complete",IF(AE{r}=0,"Not Started","In Progress"))))'

        # Remark (AI)
        ws.cell(row=r, column=COL_MAP['remark']).value = p.get('remark')

def save_document_plan(projects_data, filepath=DEFAULT_DOCUMENT_PLAN):
    """
    Saves projects_data directly into PD207_Document_Plan_Filled_Status.xlsx
    keeping ALL 602 formulas, borders, and styles intact.
    Automatically creates a timestamped backup in /backups folder.
    """
    backup_dir = os.path.join(os.path.dirname(filepath), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"PD207_backup_{ts}.xlsx")
    shutil.copy2(filepath, backup_file)

    wb = openpyxl.load_workbook(filepath, data_only=False)
    ws = wb['QG_Status']

    populate_sheet_with_projects(ws, projects_data)

    wb.save(filepath)
    return backup_file

def export_document_plan_bytes(projects_data, template_path=DEFAULT_DOCUMENT_PLAN):
    """Generates an in-memory Excel workbook (.xlsx bytes) for direct download in Streamlit."""
    wb = openpyxl.load_workbook(template_path, data_only=False)
    ws = wb['QG_Status']

    populate_sheet_with_projects(ws, projects_data)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

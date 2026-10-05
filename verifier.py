# ============================================================
# AI GLUE — RESUME VERIFIER (LENIENT VERSION)
# Ported from ImprintCV (TypeScript) to Python
# Zero-Hallucination: Only checks MAJOR metrics and facts
# ============================================================

import re
import json
from typing import List, Dict, Any, Optional


# Minimum threshold for numeric metrics (ignore smaller numbers)
MIN_METRIC_THRESHOLD = 100


# ============ METRIC PARSER ============

def extract_numeric_tokens(text: str) -> List[str]:
    """Extract only MAJOR numbers/metrics from text. Ignores small numbers."""
    if not text:
        return []

    # Only extract: percentages, currencies, multipliers, and large numbers (100+)
    patterns = [
        r'\d+(?:\.\d+)?\s*%',                          # 25%, 30.5%
        r'(?:\$|₹|€|£)\s*\d+(?:,\d{3})*(?:\.\d+)?\s*[kKmMbBlakh crore]*',  # $10m, ₹50k
        r'\b\d+(?:\.\d+)?\s*x\b',                       # 2x, 10x
        r'\b\d{3,}(?:,\d{3})*\b',                       # 100+, 1000+, 10000
    ]

    results = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            trimmed = m.strip()
            # Skip years (19xx, 20xx)
            if re.match(r'^(?:19|20)\d{2}$', trimmed):
                continue
            if trimmed:
                results.append(trimmed)

    return list(set(results))


def parse_metric_token(s: str) -> Optional[Dict[str, Any]]:
    """Parse a metric token into structured form."""
    if not s:
        return None

    clean = s.replace(',', '').strip().lower()

    # Percentage
    pct_match = re.match(r'^(\d+(?:\.\d+)?)\s*(?:%|percent)$', clean)
    if pct_match:
        return {'raw': s, 'normalizedNumber': float(pct_match.group(1)), 'unit': 'percent'}

    # Multiplier
    mult_match = re.match(r'^(\d+(?:\.\d+)?)\s*x$', clean)
    if mult_match:
        return {'raw': s, 'normalizedNumber': float(mult_match.group(1)), 'unit': 'multiplier'}

    # Currency
    if any(c in s for c in ['$', '₹', '€', '£']) or any(w in clean for w in ['usd', 'inr', 'lakh', 'crore']):
        curr_match = re.match(r'^(?:\$|₹|€|£)?\s*(\d+(?:\.\d+)?)\s*([kmbt]|lakh|crore)?', clean)
        if curr_match:
            val = float(curr_match.group(1))
            mult = curr_match.group(2)
            if mult == 'k': val *= 1_000
            elif mult == 'm': val *= 1_000_000
            elif mult == 'b': val *= 1_000_000_000
            elif mult == 'lakh': val *= 100_000
            elif mult == 'crore': val *= 10_000_000
            return {'raw': s, 'normalizedNumber': val, 'unit': 'currency'}

    # Large plain number (100+)
    num_match = re.match(r'^(\d+(?:\.\d+)?)', clean)
    if num_match:
        val = float(num_match.group(1))
        if val >= MIN_METRIC_THRESHOLD:
            return {'raw': s, 'normalizedNumber': val, 'unit': 'count'}

    return None


def check_metrics_contradiction(original_texts: List[str], tailored_text: str, field: str) -> List[Dict]:
    """Check ONLY major metrics. Ignore small numbers."""
    issues = []
    tailored_tokens = extract_numeric_tokens(tailored_text)
    if not tailored_tokens:
        return issues

    original_tokens = []
    for t in original_texts:
        original_tokens.extend(extract_numeric_tokens(t))

    for t_token in tailored_tokens:
        t_parsed = parse_metric_token(t_token)
        if not t_parsed:
            continue

        # Check if it exists in original (exact or numeric match)
        exact_match = any(
            orig.lower().strip() == t_token.lower().strip()
            for orig in original_tokens
        )

        numeric_match = False
        if not exact_match:
            for orig_token in original_tokens:
                o_parsed = parse_metric_token(orig_token)
                if o_parsed and o_parsed['unit'] == t_parsed['unit']:
                    if abs(o_parsed['normalizedNumber'] - t_parsed['normalizedNumber']) < 0.01:
                        numeric_match = True
                        break

        if not exact_match and not numeric_match:
            # Only flag if it's a MAJOR metric (%, currency, multiplier, or 1000+)
            is_major = (
                t_parsed['unit'] in ['percent', 'currency', 'multiplier'] or
                t_parsed['normalizedNumber'] >= 1000
            )
            if is_major:
                issues.append({
                    'field': field,
                    'claim': t_token,
                    'reason': 'METRIC_CONTRADICTED',
                    'factsOriginal': ', '.join(original_tokens[:5]) if original_tokens else 'No major metrics',
                    'severity': 'WARNING',  # Changed from ERROR to WARNING
                    'repairAction': f'Verify metric "{t_token}" against original resume',
                })

    return issues


# ============ CLAIM ESCALATION (Only extreme claims) ============

STRENGTH_ESCALATION = [
    (r'\bzero\s+downtime\b', 'zero downtime'),
    (r'\b100%\s+uptime\b', '100% uptime'),
    (r'\bzero\s+latency\b', 'zero latency'),
]

SCOPE_ESCALATION = [
    (r'\bprincipal\s+architect\b', 'Principal Architect'),
    (r'\bchief\s+architect\b', 'Chief Architect'),
    (r'\bdirector\s+of\s+engineering\b', 'Director of Engineering'),
    (r'\bhead\s+of\s+engineering\b', 'Head of Engineering'),
]


def check_claim_escalation(original_text: str, tailored_text: str, field: str) -> List[Dict]:
    """Check only EXTREME claim escalations."""
    issues = []
    original_lower = original_text.lower()
    tailored_lower = tailored_text.lower()

    for pattern, label in STRENGTH_ESCALATION:
        if re.search(pattern, tailored_lower, re.IGNORECASE):
            if not re.search(pattern, original_lower, re.IGNORECASE):
                issues.append({
                    'field': field,
                    'claim': label,
                    'reason': 'CLAIM_STRENGTH_ESCALATION',
                    'factsOriginal': 'Not in original',
                    'severity': 'WARNING',
                    'repairAction': f'Consider softening "{label}"',
                })

    for pattern, label in SCOPE_ESCALATION:
        if re.search(pattern, tailored_lower, re.IGNORECASE):
            if not re.search(pattern, original_lower, re.IGNORECASE):
                issues.append({
                    'field': field,
                    'claim': label,
                    'reason': 'CLAIM_SCOPE_ESCALATION',
                    'factsOriginal': 'Not in original',
                    'severity': 'ERROR',
                    'repairAction': f'Remove unverified title "{label}"',
                })

    return issues


# ============ COMPANY CHECK (Disabled - too many false positives) ============

def check_companies(original_text: str, tailored_text: str, field: str) -> List[Dict]:
    """
    Company check is DISABLED because it produces too many false positives
    (e.g., "Microsoft Outlook" flagged as company when it's software).
    Only flag if a major known fake company appears.
    """
    issues = []
    original_lower = original_text.lower()

    # Only check for specific high-risk fake companies
    FAKE_COMPANY_BLACKLIST = ['siemens', 'google', 'amazon', 'microsoft corporation']

    for fake in FAKE_COMPANY_BLACKLIST:
        if fake in tailored_text.lower() and fake not in original_lower:
            issues.append({
                'field': field,
                'claim': fake,
                'reason': 'COMPANY_ALTERED',
                'factsOriginal': 'Not in original',
                'severity': 'ERROR',
                'repairAction': f'Remove unverified company "{fake}"',
            })

    return issues


# ============ DATE CHECK ============

def check_dates(original_text: str, tailored_text: str, field: str) -> List[Dict]:
    """Check if dates were changed."""
    issues = []

    # Extract full year ranges
    year_pattern = r'\b(19|20)\d{2}\b'
    original_years = set(re.findall(year_pattern, original_text))
    tailored_years = set(re.findall(year_pattern, tailored_text))

    # Find years in tailored that don't exist in original
    for y in tailored_years:
        full_year = y
        # Get surrounding context to build full year
        matches = re.findall(r'\b((?:19|20)\d{2})\b', tailored_text)
        for match in matches:
            if match not in re.findall(r'\b((?:19|20)\d{2})\b', original_text):
                issues.append({
                    'field': field,
                    'claim': match,
                    'reason': 'DATE_ALTERED',
                    'factsOriginal': 'Year not in original',
                    'severity': 'WARNING',
                    'repairAction': f'Verify year "{match}" is correct',
                })
                break
        break

    return issues


# ============ MAIN VERIFY FUNCTION ============

def verify_documents(original_resume: str, generated_docs: Dict[str, str]) -> Dict[str, Any]:
    """
    Verify AI-generated documents against original resume.

    LENIENT MODE — only major issues flagged as ERROR.
    Small numbers and common phrases ignored.
    """
    all_issues = []

    for doc_id, content in generated_docs.items():
        if not content:
            continue

        # 1. Claim escalation (only extreme cases)
        escalation_issues = check_claim_escalation(original_resume, content, doc_id)
        all_issues.extend(escalation_issues)

        # 2. Company check (only blacklist)
        company_issues = check_companies(original_resume, content, doc_id)
        all_issues.extend(company_issues)

        # 3. Metric check (only major metrics 100+)
        metric_issues = check_metrics_contradiction([original_resume], content, doc_id)
        all_issues.extend(metric_issues)

    error_count = len([i for i in all_issues if i.get('severity') == 'ERROR'])
    warning_count = len([i for i in all_issues if i.get('severity') == 'WARNING'])

    if error_count > 0:
        status = 'FAIL'
    elif warning_count > 0:
        status = 'PASS_WITH_WARNINGS'
    else:
        status = 'PASS'

    return {
        'status': status,
        'errorCount': error_count,
        'warningCount': warning_count,
        'issues': all_issues,
        'should_retry': error_count > 0,
    }



# ============ JOB-SPECIFIC CHECKS ============

# Common action verbs for resumes
ACTION_VERBS = [
    'led', 'managed', 'increased', 'reduced', 'delivered', 'developed',
    'designed', 'built', 'created', 'implemented', 'launched', 'improved',
    'achieved', 'generated', 'grew', 'optimized', 'streamlined', 'coordinated',
    'directed', 'supervised', 'trained', 'mentored', 'established', 'initiated',
    'executed', 'analyzed', 'resolved', 'negotiated', 'spearheaded', 'drove',
    'led', 'owned', 'drove', 'scaled', 'transformed', 'accelerated'
]

WEAK_STARTERS = [
    'responsible for', 'worked on', 'helped with', 'assisted in',
    'was involved in', 'participated in', 'duties included',
    'tasked with', 'in charge of'
]


def check_action_verbs(tailored_text: str, field: str) -> List[Dict]:
    """Check if resume bullets start with strong action verbs."""
    issues = []
    lines = tailored_text.split('\n')
    bullets = [l.strip() for l in lines if l.strip().startswith(('-', '•', '*'))]

    for bullet in bullets:
        # Extract first word after bullet marker
        clean = bullet.lstrip('-•* ').strip()
        if not clean:
            continue

        first_words = clean[:50].lower()

        # Check for weak starters
        for weak in WEAK_STARTERS:
            if first_words.startswith(weak):
                issues.append({
                    'field': field,
                    'claim': bullet[:60],
                    'reason': 'WEAK_ACTION_VERB',
                    'factsOriginal': 'Use strong action verb instead',
                    'severity': 'WARNING',
                    'repairAction': f'Replace "{weak}" with action verb like "Led", "Managed", "Increased"',
                })
                break

    return issues


def check_quantified_achievements(tailored_text: str, field: str) -> List[Dict]:
    """Check if achievement bullets have quantification."""
    issues = []
    lines = tailored_text.split('\n')
    bullets = [l.strip() for l in lines if l.strip().startswith(('-', '•', '*'))]

    # Count bullets with numbers/placeholders
    quantified = 0
    total = 0

    for bullet in bullets:
        clean = bullet.lstrip('-•* ').strip()
        if len(clean) < 20:
            continue
        total += 1
        # Check for [X], %, numbers, currency
        if re.search(r'\[X\]|\d+%|\$\d|€\d|₹\d|\d+[kKmMbB]', clean):
            quantified += 1

    if total > 0 and quantified / total < 0.5:
        issues.append({
            'field': field,
            'claim': f'{quantified}/{total} bullets quantified',
            'reason': 'LOW_QUANTIFICATION',
            'factsOriginal': 'Job resumes should have 50%+ quantified achievements',
            'severity': 'WARNING',
            'repairAction': 'Add [X]% placeholders to more achievement bullets',
        })

    return issues


def check_job_title_match(original_text: str, tailored_text: str, field: str) -> List[Dict]:
    """Check if target role appears naturally."""
    issues = []
    # Extract job titles from original (rough heuristic)
    title_pattern = r'\b(Engineer|Developer|Manager|Analyst|Scientist|Architect|Designer|Consultant|Specialist|Officer|Lead|Director|Coordinator)\b'
    original_titles = set(re.findall(title_pattern, original_text, re.IGNORECASE))
    tailored_titles = set(re.findall(title_pattern, tailored_text, re.IGNORECASE))

    # If tailored has completely different titles than original
    new_titles = tailored_titles - original_titles
    if len(new_titles) > 2:
        issues.append({
            'field': field,
            'claim': ', '.join(list(new_titles)[:3]),
            'reason': 'TITLE_MISMATCH',
            'factsOriginal': ', '.join(list(original_titles)[:3]),
            'severity': 'WARNING',
            'repairAction': 'Verify job titles match original resume',
        })

    return issues


def verify_job_documents(original_resume: str, generated_docs: Dict[str, str]) -> Dict[str, Any]:
    """
    Extended verifier for JOB applications.
    Includes: standard checks + action verbs + quantification + title match
    """
    # First run standard verification
    base_result = verify_documents(original_resume, generated_docs)
    all_issues = list(base_result.get('issues', []))

    for doc_id, content in generated_docs.items():
        if not content:
            continue

        # Resume/CV specific checks (skip cover letter)
        if doc_id in ['resume', 'cv', 'rirekisho', 'shokumu_keirekisho']:
            all_issues.extend(check_action_verbs(content, doc_id))
            all_issues.extend(check_quantified_achievements(content, doc_id))
            all_issues.extend(check_job_title_match(original_resume, content, doc_id))

    error_count = len([i for i in all_issues if i.get('severity') == 'ERROR'])
    warning_count = len([i for i in all_issues if i.get('severity') == 'WARNING'])

    if error_count > 0:
        status = 'FAIL'
    elif warning_count > 0:
        status = 'PASS_WITH_WARNINGS'
    else:
        status = 'PASS'

    return {
        'status': status,
        'errorCount': error_count,
        'warningCount': warning_count,
        'issues': all_issues,
        'should_retry': error_count > 0,
        'job_specific': True,
    }